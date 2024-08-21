from flask import Flask, render_template, request, redirect, url_for
import os
import supabase
from supabase import create_client, Client

url: str = os.environ.get("SUPABASE_URL")
key: str = os.environ.get("SUPABASE_KEY")
supabase: Client = create_client(url, key)

# data = supabase.auth.sign_in_with_password({"email": "ameyapanchal011@gmail.com", "password": "sampleuser"})


class Character: 
    def __init__(self, coreTrait) -> None:
        self.dict = coreTrait
        self.Name = coreTrait["Name"]
        self.Age = coreTrait["Age"]
        self.Birthdate = coreTrait["Birthdate"]
        self.Defense = coreTrait["Defense"]
        self.Description = coreTrait["Description"]

    def __str__(self) -> str:
        return "\n-" + self.Name + "\n-" + str(self.Age) + "\n-" + self.Birthdate + "\n-" + self.Defense + "\n-" + self.Description
    
class NuancedCharacter(Character):
    def __init__(self, coreTrait, nonCoreTrait) -> None: 
        super().__init__(coreTrait)
        for key, value in nonCoreTrait.items():
            setattr(self, key, value)

    def __str__(self) -> str: 
        return "\n" + "\n".join(f"- {key}: {value}" for key, value in self.__dict__.items() if key != "dict")
    
class DBNuancedCharacter(Character): 
    def __init__(self, coreTrait, nonCoreTrait) -> None: 
        self.id = coreTrait["id"]
        super().__init__(coreTrait)
        self.Introduced = coreTrait["introduced"]
        for key, value in nonCoreTrait.items():
            setattr(self, key, value)

    def __str__(self) -> str: 
        return "\n" + "\n".join(f"- {key}: {value}" for key, value in self.__dict__.items() if key != "dict")
        
        
    
class CharacterList(): 
    def __init__(self, fileArr) -> None:
        self.ogDict = fileArr
        self.characters = {}
        k = 0
        for i in range(0, len(fileArr), 2):
            self.characters[k] = NuancedCharacter(fileArr[i], fileArr[i+1])
            k+=1
            
    def __str__(self) -> str:
        return "\n\n".join(f"- {key}: {value}" for key, value in self.characters.items() if value != "")
    
    def __setitem__(self, key, value):
        setattr(self, key, value)

    def __getitem__(self, key):
        return getattr(self, key)
  
    def filter(self, trait, val) -> str:
        retDict = CharacterList({})
        for key, value in self.characters.items():
            if val == "" or not val:
                if(hasattr(value, trait)):
                    retDict.characters[key] = value
            elif trait == "Description":
                if val.lower() in getattr(value, trait).lower():
                    retDict.characters[key] = value
            elif hasattr(value, trait) and getattr(value, trait) == val:
                retDict.characters[key] = value
        return retDict
    
    def getAllValues(self) -> str:
        values = {"Name": set(), "Age": set(), "Birthdate": set(), "Defense": set(), "NonCore": set()}
        for key, value in self.characters.items():
            values["Name"].add(getattr(value, "Name"))
            values["Age"].add(getattr(value, "Age"))
            values["Birthdate"].add(getattr(value, "Birthdate"))
            values["Defense"].add(getattr(value, "Defense"))

            for k, v in value.__dict__.items():
      
                if k != "dict" and k != "Name" and k != "Age" and k != "Birthdate" and k != "Defense" and k != "Description":
                    if(k not in values["NonCore"]):
                        values["NonCore"].add(k)
        for key, value in values.items():
            values[key] = sorted(values[key])
        return values
    
    def sort(self, method) -> str:
        self.characters = dict(sorted(self.characters.items(), key=lambda item: item[1].__dict__[method]))
        return self
    
    def getOGDict(self) -> str:
        return self.ogDict
    
    def returnDict(self) -> str: 
        return self.characters
        
class DBCharacterList(CharacterList): 
    def __init__(self, isAuthor) -> None: 
        self.isAuthor = isAuthor
        self.characters = {}
        if(self.isAuthor):
            self.data = supabase.table("Character List").select("*").execute()
        else:
            self.data = supabase.table("Character List").select("*").eq("introduced", True).execute()
        for i in range(len(self.data.data)):
            self.extra = self.data.data[i]["Additional"]
            self.characters[i] = DBNuancedCharacter(self.data.data[i], self.data.data[i]["Additional"])

    def __str__(self) -> str:
        return "\n\n".join(f"- {key}: {value}" for key, value in self.characters.items() if value != "")

    def id(self, loc) -> str:
        return self.data


    
    # def upload(self) -> None: 
    #     for i in range(0, len(self.characterDict)-1, 2):
    #         character = self.characterDict[i]
    #         intro = 1 if character["Introduced"] == "Yes" else 0
    #         extra = self.characterDict[i+1]
    #         response = (
    #             supabase.table("Character List")
    #             .insert({"Name": character["Name"], "Age": character["Age"], "Birthdate": character["Birthdate"], "Defense": character["Defense"], "Description": character["Description"], "Introduced": intro, "Additional": extra})
    #             .execute()
    #         )
    

        

            


      


f = open("sample.txt", encoding='utf8')

files = f.read()

fileParas = files.split("\n\n")

# creating dict
dicty = {}

for i in range(len(fileParas)): 
    char = fileParas[i].split("\n")
    dicty[i] = {}
    for k in range(len(char)):
        line = char[k].split(":")
        if len(line) == 2:
            cate = line[0].strip()
            val = line[1].strip()
            dicty[i][cate] = val


characters = CharacterList(dicty)




app = Flask(__name__)

@app.route("/", methods=["GET", "POST"])
def signIn():
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("pass") 
        
        try:
            data = supabase.auth.sign_in_with_password({"email": email, "password": password})
            user = supabase.auth.get_user()
            if(user):
                return redirect(url_for('index'))
        except:
            print("wrong email or password")
        
        
    return render_template('signIn.html')

@app.route("/add", methods=["GET", "POST"])
def add():
    if request.method == "POST":
        name = request.form.get("name")
        age = request.form.get("age") 
        birth = request.form.get("birth")
        deff = request.form.get("deff") 
        desc = request.form.get("desc")
        extra = {}
        response = (
            supabase.table("Character List")
            .insert({"Name": name, "Age": age, "Birthdate": birth, "Defense": deff, "Description": desc, "introduced": 1, "Additional": extra})
            .execute()
        )
        return redirect(url_for('index'))
    return render_template('add.html')

@app.route("/update", methods=["GET", "POST"])
def update():
    user_info = supabase.table("User Information").select("*").execute()
    isUserAuthor = user_info.data[0]['isAuthor']
    char = DBCharacterList(isUserAuthor)
    id = request.args.get("id")
    realId = char.returnDict()[int(id)].id
    if request.method == "POST":
        name = request.form.get("name")
        age = request.form.get("age") 
        birth = request.form.get("birth")
        deff = request.form.get("deff") 
        desc = request.form.get("desc") 
        intro = request.form.get("intro")
        extra = char.extra
        response = (
            supabase.table("Character List")
            .update({"Name": name, "Age": int(age), "Birthdate": birth, "Defense": deff, "Description": desc, "Additional": extra, "introduced": int(intro)})
            .eq("id", int(realId))
            .execute()
        )
        return redirect(url_for('index'))

    return render_template('update.html', data=char.returnDict()[int(id)], fakeId=id)

@app.route("/index", methods=["GET", "POST"])
def index(): 
    user = supabase.auth.get_user()
    user_info = supabase.table("User Information").select("*").execute()
    isUserAuthor = user_info.data[0]['isAuthor']

    newChar = DBCharacterList(isUserAuthor)

    if request.method == "POST":
        char = DBCharacterList(isUserAuthor)
        name = request.form.get("name")
        age = request.form.get("age")
        birth = request.form.get("birth")
        deff = request.form.get("def") 
        desc = request.form.get("desc") 
        sort = request.form.get("sort")
        nonCoreKey = request.form.get("nonCoreKey")
        nonCoreVal = request.form.get("nonCoreValue")
        arr = {"Name": name, "Age": age, "Birthdate": birth, "Defense": deff, "Description": desc}
        for key, value in arr.items():
           if value and len(value) > 0:
               if(key == "Age"):
                   value = int(value)
               char = char.filter(key, value) 
        if nonCoreKey and nonCoreVal and len(nonCoreKey) > 0 and len(nonCoreVal) > 0:
            char = char.filter(nonCoreKey, nonCoreVal)
        if sort and len(sort) > 0:
            char = char.sort(sort)     
        return render_template('index.html', name=char.returnDict(), data=newChar.getAllValues(), isAuthor=isUserAuthor)
    return render_template('index.html', name=newChar.returnDict(), data=newChar.getAllValues(), isAuthor=isUserAuthor) #

