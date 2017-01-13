class SearchParameters:
    def __init__(self):
        self.dict = {}
        self.addSinceId()
        self.requiredAttributes = ['collection', 'keywords']
        for attr in self.requiredAttributes:
            self.dict[attr] = None
    
    def addKeywords(self, keywordList):
        self.dict['keywords'] = keywordList
        
    def addLocation(self, location):
        self.dict['location'] = location
    
    def addCollectionName(self, collection_name):
        self.dict['collection'] = collection_name
    
    def addSinceId(self, since_id=1):
        self.dict['since_id'] = since_id
    
    def searchParametersReady(self):
        ready = True
        for attr in self.requiredAttributes:
            if not (attr):
                ready = False
                break         
        return ready
    
    def getDict(self):
        return self.dict
    
    def getCollectionName(self):
        return self.dict['collection']