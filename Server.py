from bottle import Bottle, run, request, response, abort
from Tree import Tree, print_tree
from peewee import DataError, DatabaseError


class HttpServer:
    def __init__(self):
        self.tree = Tree()

        self.app = Bottle()

        @self.app.get('/')
        def get():

            try:
                path = request.GET.get("path")
                if path is None:
                    abort(400, "")
                node_id = self.get_id(path)

                result = self.tree.get_data_of_element(node_id)
                return result
            except IndexError:
                return "Incorrect index"
            except DatabaseError:
                return "Incorrect path"

        @self.app.post('/')
        def post():
            try:
                path = request.GET.get("path")
                name = request.GET.get("name")
                data = request.GET.get("data")

                if path is None or name is None or data is None:
                    abort(400, "")

                node_id = self.get_id(path)
                self.tree.post(name, node_id, data)
                return "OK"
            except IndexError:
                return "Incorrect index"
            except DataError:
                return "Incorrect name"

        @self.app.put('/')
        def put():
            try:
                print_tree()
                path = request.GET.get("path")
                name = request.GET.get("name")
                data = request.GET.get("data")

                if path is None or name is None or data is None:
                    abort(400, "")

                node_id = self.get_id(path)
                self.tree.put(name, node_id, data)
                return "OK"

            except IndexError:
                return "Incorrect index"
            except DataError:
                return "Incorrect name"

        @self.app.delete('/')
        def delete():
            try:
                path = request.GET.get("path")
                node_id = self.get_id(path)
                self.tree.delete(node_id)

                if path is None:
                    abort(400, "")

                return "OK"
            except IndexError:
                return "Incorrect index"
            except DataError:
                return "Incorrect name"


    def get_id(self, path_str):
        path = path_str.split('/')
        return self.tree.get_element_id(path)


if __name__ == '__main__':
    server = HttpServer()
    host = '0.0.0.0'
    port = 8080
    run(server.app, host=host, port=port)
