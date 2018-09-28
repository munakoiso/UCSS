import re
from peewee import SqliteDatabase, CharField, IntegerField, Model, ForeignKeyField, DataError, DatabaseError

db = SqliteDatabase('Tree.db')


def print_tree():
    for e in Node.select():
        print(e.name)
    print('___')
    for e in Parent.select():
        print(e.parent_id.get_id(), e.children_id.get_id())
    print('___')


class Node(Model):

    name = CharField()
    data = CharField(null=True)

    @staticmethod
    def is_contain_id(node_id):
        return len(Node.select().where(Node.id == node_id)) != 0

    class Meta:
        database = db


class Parent(Model):
    children_id = ForeignKeyField(model=Node)
    parent_id = ForeignKeyField(model=Node)

    @staticmethod
    def get_parent_id(children_id):
        print(children_id)
        if not Node.is_contain_id(children_id):
            raise DataError('Id not exist in database')

        parent = Parent.select().where(Parent.children_id == children_id).get()
        return parent.parent_id.get_id()

    @staticmethod
    def get_childrens_id(parent_id):
        if not Node.is_contain_id(parent_id):
            raise DataError('Id not exist in database')
        result = []
        for e in Parent.select().where(Parent.parent_id == parent_id):
            result.append(e.get_id())
        return result

    class Meta:
        database = db


class Tree:
    def __init__(self):

        Node.create_table(safe=True)
        Parent.create_table(safe=True)
        if not Node.is_contain_id(0):
            Node.create(name='', id=0)
            Node.create(name='.')
            Parent.create(parent_id=0, children_id=1)

    def get_element_id(self, names):
        current_id = 0
        for name in names:
            is_children_exist = False
            for children_id in Parent.get_childrens_id(current_id):
                if Node.get_by_id(children_id).name == name:
                    current_id = children_id
                    is_children_exist = True
                    break
            if not is_children_exist:
                raise DatabaseError('Incorrect path')
        return current_id

    def get_elements(self, node_id):
        elements = []
        if not Node.is_contain_id(node_id):
            raise IndexError('Id not exist in database')
        for children_id in Parent.get_childrens_id(node_id):
            elements.append(Node.get_by_id(children_id))
        return elements

    def get_data_of_element(self, node_id):
        if not Node.is_contain_id(node_id):
            raise IndexError('Id not exist in database')
        node = Node.get_by_id(node_id)
        return "{} - {}".format(node.name, node.data)

    def put(self, name, node_id=0, data=None):
        if not Node.is_contain_id(node_id):
            raise IndexError('Id not exist in database')
        parent = Node.get_by_id(node_id)
        if not Tree.is_name_correct(name, node_id):
            raise DataError("Name isn't corrent")
        parent_id = parent.get_id()
        new_element = Node.create(name=name, data=data)
        new_id = new_element.get_id()
        Parent.create(children_id=new_id, parent_id=parent_id)

    def post(self, name, node_id, data=None):
        if not Node.is_contain_id(node_id):
            raise IndexError('Id not exist in database')
        element = Node.get_by_id(node_id)
        if not Tree.is_name_correct(name, Parent.get_parent_id(node_id), element.id):
            raise DataError("Name isn't correct")

        element.data = data
        element.name = name
        element.save()

    def delete(self, node_id, delete_prev_edges=True):
        edges_id = []
        for edge in Parent.select().where(Parent.parent_id == node_id):
            children_id = edge.children_id.get_id()
            self.delete(children_id, False)
            edges_id.append(edge.get_id())

        Node.delete_by_id(node_id)
        if delete_prev_edges:
            for edge in Parent.select().where(Parent.children_id == node_id):
                edges_id.append(edge.get_id())
        for edge_id in edges_id:
            Parent.delete_by_id(edge_id)

    @staticmethod
    def is_name_correct(name, parent_id, current_id=None):
        for children_id in Parent.get_childrens_id(parent_id):
            if Node.get_by_id(children_id).name == name:
                if children_id != current_id:
                    return False
        return re.match(r'([a-zA-Zа-яА-Я]+ )*[a-zA-Zа-яА-Я]+', name) and \
               not Tree.is_name_in_branch(name, parent_id)

    @staticmethod
    def is_name_in_branch(name, parent_id):

        if parent_id == 0:
            return False

        return Node.get_by_id(parent_id).name == name or \
               Tree.is_name_in_branch(name, Parent.get_parent_id(parent_id))
