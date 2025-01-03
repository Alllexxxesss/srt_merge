import re, sys,locale


#file1 = r".\srt\eng_ansi.srt"
#file2 = r".\srt\rus_ansi.srt"
#file3 = r".\srt\new_ansi.srt"

START_DELTA: float = 0.1
END_DELTA: float = 0.1
MINIMUM_DELTA: float = 0.1
PATTERN1: str = r'\d\d[:]\d\d[:]\d\d[,]\d\d\d[ ][-][-][>][ ]\d\d[:]\d\d[:]\d\d[,]\d\d\d'
count_f1: int = 1
count_f2: int = 1

# словарик с кодами ошибок
error_dict = {
    1: "ошибка формата оригинального файла  "
    
    , 2:"ошибка формата файла перевода "
    , 4:"не правильный вызов программы - subt 'путь к оригинальному файлу субтитров' 'путь к файлу субтитров с переводом' 'путь к выходному файлу субтитров' [кодировка файлов (по умолчанию - системная локаль)]" }

def error_trap (error_code) -> None: 
    print (f"Error (code {error_code}) ",error_dict[error_code])
    sys.exit (1)
    

def readblock (file,flag:bool,file_out):
    
    global count_f1,count_f2,ID
    
    text =""
    string = file.readline()
    if not string :
                                                                                                                                                                                    #eof ?
        return 0,0,0,0,0

    error_code = 2**flag                                                                                                                                                    #set error code 1 or 0 depends on witch file is reading
    tmpstring = string[0:len(string)-1]
                                                                                                                                                                                    #check if first string is ID
    if not (tmpstring.isdigit()):
          
          error_trap (error_code)
    if flag:                                                                                                                                                                        # with file: original (0) or translate (1) ?
        if int(string) !=count_f2:                                   
            error_trap (error_code)
        
        count_f2 +=1
    else:
        if int(string) !=count_f1:                                   
            error_trap (error_code)
        string = str (ID)
        string = string + chr (10)                                                                                                                                            # ID for output file
        count_f1 +=1
         
    text = text + string    
    string = file.readline()
    text = text + string
    
    if not (re.search(PATTERN1,string)):                                                                                                                                # check if string is timer string
         error_trap (error_code)            

    start = (int (string[0:2]))*(10**4) + (int (string[3:5]))*(10**2) + (int (string[6:8]))*(10**0)+(int (string[9:12]))*10**(-3)
    end = (int (string[17:19]))*(10**4) + (int (string[20:22]))*(10**2) + (int(string[23:25]))*(10**0)+(int (string[26:29]))*10**(-3)     
    delta = end - start
   
    if delta <MINIMUM_DELTA:                                                                                                                                             # if sub timer delta to small then error
         error_trap (error_code)
    
    string = ''
    subtext =""
    new_line = 0
    pre_string = "start_string"

   
    while True:
           
          string = file.readline()
          subtext = subtext + string                                                                                                                                            #  sub text 
          text = text + string                                                                                                                                                      
          
          if ord (string [0]) == 10  and  ord (pre_string [-1]) == 10:                                                                                                  #check if end of sub text
              break
          pre_string = string

    return string, text,start,end,subtext    


file_encoding = locale.getpreferredencoding()
if len (sys.argv) < 4:                                                                                                                                                             # check for command line args
    error_trap (error_code = 4)
else:
    file1,file2,file3 = sys.argv[1], sys.argv[2],sys.argv[3]
    error_dict[1] = error_dict[1]+file1                                                                                                                                       # add to error dict file name
    error_dict[2] = error_dict[2]+file2
    if len (sys.argv) == 5 :
        file_encoding = sys.argv[4]
    print (file1,file2,file3)

    

with open(file1, 'r',encoding=file_encoding,errors='ignore' ) as f1, open(file2, 'r',encoding=file_encoding,errors='ignore' ) as f2, open (file3,'w') as f3 :
                                                                                                                                                                                           
       
    i = 0
    ID = 1
    while True:                                                                                                                                                                          #  read line by line from file until error or eof
        string,text,start_timer1,end_timer1,subtext = readblock (f1,0,f3)
        while True:
            string2,text2,start_timer2,end_timer2,subtext = readblock (f2,1,f3)
            if (abs (start_timer1 - start_timer2) < START_DELTA) and ((end_timer1 - end_timer2) < END_DELTA) and text and text2:
               text = text [0:-1]
               f3.write(text)                                                                                                                                                              #original sub
               f3.write(subtext)                                                                                                                                                        #sub translated
         
               f2.seek (0)
               count_f2 = 1
               ID +=1
               break
            
            if not string2:
                f2.seek (0)
                count_f2 = 1
                break
        

        i +=1
        
        if not string:
            break
        
print ("merged subs in ",file3," - ",ID-1)
print ("original subs in ",file1," - ", i-1)
