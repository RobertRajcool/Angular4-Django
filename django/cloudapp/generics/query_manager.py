
# Format result data of cursor execution from tuple into dict


def dictfetchall(cursor):
    "Return all rows from a cursor as a dict"
    columns = [col[0] for col in cursor.description]
    return [
        dict(zip(columns, row))
        for row in cursor.fetchall()
        ]


def CONTAINS_QUERY(field_name, lookup_value):
    """ Constructs LIKE lookup for JSON field """

    query = "`{}` LIKE %s".format(field_name)

    return query, lookup_value


def JSON_CONTAINS_QUERY(field_name, lookup_value):
    """ Constructs LIKE lookup for JSON field """
    field_name_sigments = field_name.split('__')

    if len(field_name_sigments) <= 0:
        raise ValueError("Invalid field %s" % field_name)
    else:
        field = field_name_sigments[0]
        json_path = '$.{}'.format('.'.join(field_name_sigments[1:]))

        query = "JSON_EXTRACT(`{}`, '{}') LIKE %s".format(field, json_path)

        return query, '%{}%'.format(lookup_value)
