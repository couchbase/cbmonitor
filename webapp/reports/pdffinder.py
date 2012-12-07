from couchdbkit import Server
from django.conf import settings


class PDFFinder():

    def __init__(self):
        self.uri = settings.COUCHDB_URI

    def url_gen(self, db_name, id, filename):
        """Generate attachment URL"""

        url = "{uri}{db_name}/{id}/{filename}"\
              .format(uri=self.uri, db_name=db_name, id=id, filename=filename)
        return url

    def all_dbs(self):
        """Database iterator"""
        databases = ("evperf2", "lucky6", "lucky8", "mixed", "read", "vperf",
                     "vperf4", "write", "xperf", "reb")

        server = Server(self.uri)
        for db_name in databases:
            yield db_name, server[db_name]

    def all_docs(self, db):
        """View iterator"""
        view = {"map": "function(doc) {emit(doc.filename, null);}"}

        view = db.temp_view(view)
        for doc in view:
            if doc["key"]:
                yield doc

    def check(self, query, filename):
        """Check search criteria"""
        for word in query:
            if word not in filename:
                return False
        return True

    def search(self, query):
        """Search for filename in predefined list of databases using ad hoc
        queries"""

        urls = list()
        for db_name, db in self.all_dbs():
            for doc in self.all_docs(db):
                filename = doc["key"]
                if self.check(query, filename):
                    url = self.url_gen(db_name, doc["id"], filename)
                    urls.append([filename, url])
        return urls
