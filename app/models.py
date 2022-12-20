from django.db import models
import os
import pandas as pd
import json
import re
import contractions
import demoji
import string
import nltk
from nltk.stem import WordNetLemmatizer
from django.core.files.base import  ContentFile

class Data(models.Model):
    name=models.CharField(max_length=255,unique=True,null=False,default='Untitled')
    text_column=models.CharField(max_length=255,null=True)
    raw_file=models.FileField(upload_to ='raw_data/',null=True)
    clean_file=models.FileField(upload_to ='clean_data/',null=True)
    cleaned=models.BooleanField(default=False)
    def __str__(self) -> str:
        return self.name
    def clean_data(self):
        # load raw data
        self.get_raw_data()
        data=self.raw_data_file
        text_col=data.loc[:,self.text_column]

        #supprimer les mots qui commencent par des symboles @ ;
        text_col = text_col.map(lambda x:re.sub('@\w*','',str(x)))
        #supprimer les caractères spéciaux sauf [a-zA-Z]
        text_col = text_col.map(lambda x:re.sub('[^a-zA-Z]',' ',str(x)))
        #supprimer le lien commence par https
        text_col = text_col.map(lambda x:re.sub('http.*','',str(x)))

        # convert to lowercase
        text_col = text_col.apply(lambda x: ' '.join([w.lower() for w in x.split()]))
        
        # remove emojis
        text_col = text_col.apply(lambda x: demoji.replace(x, ""))
        
        # expand contractions  
        text_col = text_col.apply(lambda x: ' '.join([contractions.fix(word) for word in x.split()]))

        # remove punctuation
        text_col = text_col.apply(lambda x: ''.join([i for i in x if i not in string.punctuation]))
        
        # remove numbers
        text_col = text_col.apply(lambda x: ' '.join(re.sub("[^a-zA-Z]+", " ", x).split()))

        # remove stopwords
        stopwords = nltk.corpus.stopwords.words('english')
        text_col = text_col.apply(lambda x: ' '.join([w for w in x.split() if w not in stopwords]))

        # lemmatization
        text_col = text_col.apply(lambda x: ' '.join([WordNetLemmatizer().lemmatize(w) for w in x.split()]))

        # remove short words
        text_col = text_col.apply(lambda x: ' '.join([w.strip() for w in x.split() if len(w.strip()) >= 2]))

        # generating new file
        data=pd.DataFrame({self.text_column:text_col})

        # saving the file 
        self.cleaned=True
        if self.clean_file:
            os.remove(self.clean_file.path)
        self.clean_file.save(self.name+'.csv', ContentFile(data.to_csv(index_label='ID')))
    def delete(self, *args, **kwargs):
        if self.raw_file:
            os.remove(self.raw_file.path)
        if self.clean_file:
            os.remove(self.clean_file.path)
        super(Data, self).delete(*args, **kwargs)
    def save(self, *args, **kwargs):
        if not self.cleaned:
            ext=self.raw_file.name.split('.')[1]
            self.raw_file.name = self.name+'.'+ext
        super(Data, self).save(*args, **kwargs)
    def get_raw_data(self):
        data_file=Data.load_raw_data(self.id,output_type='csv')
        self.raw_data_file=data_file
    def get_clean_data(self):
        data_file=Data.load_clean_data(self.id,output_type='csv')
        self.clean_data_file=data_file
    @classmethod
    def get_data(cls,id):
        return cls.objects.get(id=id)
    @classmethod
    def get_all(cls,):
        return cls.objects.all()
    @classmethod
    def save_data(cls,name,column,file):
        try:
            obj=cls(name=name,text_column=column,raw_file=file)
            obj.save()
            return True
        except Exception as e:
            print(e)
        return False
    @classmethod
    def load_raw_data(cls,id,output_type='json',limit=None):
        data=None
        try:
            obj=cls.get_data(id)
            filename=obj.raw_file.name
            if filename.endswith('.csv'):
                if limit:
                    if output_type == 'json':
                        data=json.loads(pd.read_csv(obj.raw_file.path,nrows=limit).to_json())
                    else:
                        data=pd.read_csv(obj.raw_file.path,nrows=limit)
                else:
                    if output_type == 'json':
                        data=json.loads(pd.read_csv(obj.raw_file.path).to_json())
                    else:
                        data=pd.read_csv(obj.raw_file.path)
            elif filename.endswith('.json'):
                data=json.loads(pd.json_normalize(json.loads(open(obj.raw_file.path, 'r').read())).to_json())
        except Exception as e:
            print(e)
        return data
    @classmethod
    def load_clean_data(cls,id,output_type='json',limit=None):
        data=None
        try:
            obj=cls.get_data(id)
            filename=obj.clean_file.name
            if filename.endswith('.csv'):
                if limit:
                    if output_type == 'json':
                        data=json.loads(pd.read_csv(obj.clean_file.path,nrows=limit).to_json())
                    else:
                        data=pd.read_csv(obj.clean_file.path,nrows=limit)
                else:
                    if output_type == 'json':
                        data=json.loads(pd.read_csv(obj.clean_file.path).to_json())
                    else:
                        data=pd.read_csv(obj.clean_file.path)
            if filename.endswith('.json'):
                data=json.loads(open(obj.clean_file.path, 'r').read())
        except Exception as e:
            print(e)
        return data
