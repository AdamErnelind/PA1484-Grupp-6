def Intialer(namn):
    resultatet = ""
    delnamn = namn.replace("-", " ").split()
    for ch in delnamn:
        resultatet += ch[0]
    return resultatet

print(Intialer("Per-Boke Hansson"))



        
    
    
            

    

