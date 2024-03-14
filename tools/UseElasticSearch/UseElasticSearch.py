from elasticsearch import Elasticsearch





class MyElasticSearch:
    def __init__(self, host, port,user=None,passwd=None):
        self._user=user
        self._passwd=passwd
        s_port=str(port) if isinstance(port,int) else port
        self._url="http://"+host+":"+s_port
        self._es=None

    def connect(self):
        if self._user and self._passwd:
            self._es = Elasticsearch([self._url],http_auth=(self._user,self._passwd))
        elif self._user:
            self._es = Elasticsearch([self._url],http_auth=self._user)
        else:
            self._es = Elasticsearch([self._url])
        if self._es.ping():
            return True
        else:
            return False
        
    def create_index(self,index_name):
        if self._es.indices.exists(index=index_name):
            return False
        else:
            self._es.indices.create(index=index_name)
            return True
        
    def delete_index(self,index_name):
        if self._es.indices.exists(index=index_name):
            self._es.indices.delete(index=index_name)
            return True
        else:
            raise Exception("index not exists")
            
        
    def insert_data(self,index_name,data):
        self._es.index(index=index_name,document=data)
    
    def delete_data_by_id(self,index_name,id):
        self._es.delete(index=index_name,id=id)

    def delete_data_by_name(self,index_name,name):
        query = {"match": {"name": name}}
        result = self._es.search(index=index_name, body=query)
        for i in result['hits']['hits']:
            self._es.delete(index=index_name,id=i['_id'])

    def search_data_by_query(self,index_name,query):
        result = self._es.search(index=index_name, body=query)
        return result
    
    def search_data(self,index_name,size:int=10):
        result = self._es.search(index=index_name,size=size)
        return result
    
    def if_index_exit(self,index_name):
        if self._es.indices.exists(index=index_name):
            return True
        return False
    
    def get_index_num(self,index_name):
        '''
        get index number
        '''
        if not self.if_index_exit(index_name):
            raise Exception("index not exists")
        ret=self.search_data(index_name,size=1) 
        return ret['hits']['total']['value']
    


