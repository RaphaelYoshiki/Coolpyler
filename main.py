import re

#Função para checar palavra e tokenizar
def checkword(word, isCommentBlock, isCommentLine, isString):
  if (word == "" or word == "\t" or word == "\n" or word == " "):
    return [], isCommentBlock, isCommentLine, isString

  matches = []#Inicia lista de correspondências
  blockif = 0#blockif ajuda a discernir as aspas que iniciam e terminam
             #uma string

  chaves = ['class', 'else', 'false', 'fi', 'if', 'in', 'inherits', 'isvoid', 'let', 'loop', 'pool', 'then', 'while', 'case', 'esac', 'new', 'of', 'not', 'true']

  simbolos = ['[', ']', '{', '}', '(', ')', '.', ',', ';', ':', '<-']

  operators = ['+', '-', '*', '/', '=', '<', '>']

  commAndString = ['--', '(*', '*)', '\"']
  
  regex = r"\"|\(\*|\*\)|\-\-|^class$|^else$|^false$|^fi$|^if$|^in$|^inherits$|^isvoid$|^let$|^loop$|^pool$|^then$|^while$|^case$|^esac$|^new$|^of$|^not$|^true$|\[|\]|\{|\}|\(|\)|\.|\,|\;|\:|\<\-|\<|\>|\+|\-|\=|\/|\*|^\d+$|^\w+$"
  
  
  p = re.compile(regex)#Compilar objeto de padrão regex
  match = p.search(word)#Retorna objeto Match
  if(match):
    corr = match.group(0)
    isInt = re.findall(r'^\d+\d$', corr)#Especificar Integer
    isID = re.findall(r'^\w+$', corr)#Especificar Identificador

    if(corr in commAndString):#Detecção de comentários e string
      if(corr == '--'):
        isCommentLine = 1
      elif(corr == '(*'):
        isCommentBlock = 1
      elif(corr == '*)'):
        isCommentBlock = 0
      elif(corr == '"' and isString == 0 and blockif == 0):
        isString = 1
        blockif = 1
        matches.append("string")
      elif(corr == '"' and isString == 1 and blockif == 0):
        isString = 0
        blockif = 1

    #Ignorar correspondências caso ignore > 0
    ignore = isCommentBlock+isCommentLine+isString
    
    if(corr in chaves and ignore == 0):#Detecção de palavras-chave
      matches.append("keyword")
      
    if(corr in simbolos and ignore == 0):#Detecção de símbolos
      if(corr == '['):
        matches.append("sqBrackOpen")
      elif(corr == ']'):
        matches.append("sqBrackClose")
      elif(corr == '{'):
        matches.append("curBrackOpen")
      elif(corr == '}'):
        matches.append("curBrackClose")
      elif(corr == '('):
        matches.append("parenOpen")
      elif(corr == ')'):
        matches.append("parenClose")
      elif(corr == '.'):
        matches.append("dot")
      elif(corr == ','):
        matches.append("comma")
      elif(corr == ';'):
        matches.append("semiColon")
      elif(corr == ':'):
        matches.append("colon")
      elif(corr == '<-'):
        matches.append("atrib")
      elif(corr == '\"'):
        matches.append("quot")

    if(isInt and ignore == 0):#Detecção de Integer
      matches.append("int")

    if(isID and not isInt and not(corr in simbolos or corr in chaves 
       or corr in operators or corr in commAndString) and ignore == 0):
      matches.append("ID")#Detecção de Identificadores

    if(corr in operators and ignore == 0):#Detecção de operadores
      matches.append("op")
  return matches, isCommentBlock, isCommentLine, isString
#Fim de função

#Código principal
source = open("sourcecode.cl", "r")
lines = source.readlines()#Ler arquivo linha por linha e armazenar em lista

tokens = []#Inicializar lista de tokens

linecount = 0#Contagem de linhas
commentBlockToggle = 0#Bloqueador bloco de comentário
commentLineToggle = 0#Bloqueador linha de comentário
stringToggle = 0#Bloqueador string

for line in lines:#Para cada linha
  linecount += 1
  commentLineToggle = 0#Reiniciar bloqueador linha de comentário
  line = re.sub(r'(\({1}\*{1}|\(|\*{1}\){1}|\)|\[|\]|\{|\}|\/|\;|\:|\.|\>|\,|\<{1}\-{1}|\<|\+|\={1}\>{1}|\=|\-{1}\-{1}|\-)', r' \1 ', str(line))#Adicionar whitespace entre símbolos
  words = re.split(' ', line)#Separar linha em palavras
  for word in words:#Para cada palavra
    #Chamada checkword, retorna lista de tokens de correspondência
    #e estado de cada bloqueador
    matches, commentBlockToggle, commentLineToggle, stringToggle = checkword(word, commentBlockToggle, commentLineToggle, stringToggle)
    if matches:#Se houver alguma correnspondência
      for match in matches:
        tokens.append(match)#Adicionar tokens na lista

print("Lista de tokens:")
print(tokens)