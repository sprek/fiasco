""" data_model
This class contains helper functions for interacting with an
sqlite3 database using a data model pattern.

Assumes that the class_name passed in to the functions has
member variables whose names match the columns in the database table
"""

def get_objects_from_db_result(class_name, db_result):
    """
    input: class_name - Class
           db_result -  sqlite3 result from a "select *" type query
    returns: list of Class objects
    """
    args_dict = {}
    cols = list_columns_from_result(db_result)
    results = db_result.fetchall()
    objects = []
    for result in results:
        for i, val in enumerate(result):
            args_dict[cols[i]] = val
        objects.append(class_name(**args_dict))
    return objects

def list_class_attributes(class_name):
    """
    input: class_name - Class
    returns: alphabetically sorted member variables for class_name
    """
    return sorted(class_name().__dict__.keys())

def list_columns_from_result(result):
    """
    input: result - sqlite3 result from a query
    returns: a list of the names for each column in the result input
             the order of the column names matches the order of the result input
    """
    return list(map(lambda x: x[0], result.description))

def get_class_vals(obj):
    """
    input: obj - object of type Class
    returns: list of member variable values of obj, sorted alphabetically by
             member variable name
    """
    vals = []
    for attr in sorted(obj.__dict__.keys()):
        vals.append(getattr(obj, attr))
    return vals

# --------------------------------------------------
# Database access functions

def get_objects_from_db(class_name, db):
    """
    input: class_name - Class
           table_name - string of table in database
           db - database
    returns: list of class_name objects in database
    """
    table_name = class_name_to_table_name(class_name)
    cur = db.cursor()
    db_result = cur.execute("SELECT * FROM " + table_name)
    return get_objects_from_db_result(class_name, db_result)

def get_object_from_db_by_key(class_name, key_name, key_val, db):
    """
    input: class_name - Class
           key_name - string of name of key column
           key_val - value of the key
           db - database
    returns: class_name object that matches the item in the database,
             or None if not found
    """
    cur = db.cursor()
    table_name = class_name_to_table_name(class_name)
    db_result = cur.execute("SELECT * FROM " + table_name + " where " + key_name + " = ?",
                            (key_val,))
    objects = get_objects_from_db_result(class_name, db_result)
    if len(objects) == 0:
        return None
    return objects[0]

def insert_object_into_db (obj, db):
    """
    input: obj - object to insert into database
           db - database
    """
    cur = db.cursor()
    table_name = class_name_to_table_name(type(obj))
    attr_list = ','.join(list_class_attributes(type(obj)))
    val_list = ','.join(list(len(list_class_attributes(type(obj))) * '?'))
    cur.execute("INSERT INTO " + table_name + " (" + attr_list + ") VALUES (" + val_list + ")",
                get_class_vals(obj))
    db.commit()

def update_object_in_db_by_key (obj, key_name, key_val, db, do_insert=True):
    cur = db.cursor()
    table_name = class_name_to_table_name(type(obj))
    if get_object_from_db_by_key (type(obj), key_name, key_val, db):
        # object exists
        attr_list = list_class_attributes(type(obj))
        set_string = ','.join('%s=?' % t for t in attr_list)
        val_list = get_class_vals(obj)
        val_list.append(key_val)
        cur.execute("UPDATE " + table_name + " SET " + set_string + " WHERE " + key_name + "=?",
                    val_list)
        db.commit()
    else:
        if do_insert:
            insert_object_into_db(obj, db)

def clear_table (class_name, db):
    """
    input: class_name - Class
    returns: db - database
    """
    table_name = class_name_to_table_name(class_name)
    cur = db.cursor()
    cur.execute('DELETE FROM ' + table_name)
    db.commit()

def clear_table_by_key (class_name, key_name, key_val, db):
    """
    input: class_name - Class, key_name - string, key_val - value of key
    returns: db - database
    """
    table_name = class_name.__name__.lower()
    cur = db.cursor()
    cur.execute('DELETE FROM ' + table_name + " where " + key_name + " = ?",
                (key_val,))
    db.commit()

def class_name_to_table_name (class_name):
    """
    input: class_name - Class
    returns: a string of the class with the first letter lowercase
    """
    class_str = class_name.__name__
    if len(class_str) == 0:
        return ''
    elif len(class_str) == 1:
        return class_str.lower()
    return class_str[0].lower() + class_str[1:]
