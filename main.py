import re
import sys

#Função para checar palavra e tokenizar
def checkword(word, isCommentBlock, isCommentLine, isString):
  if (word == "" or word == "\t" or word == "\n" or word == " " or word == "\r"):
    return [], isCommentBlock, isCommentLine, isString

  matches = []#Inicia lista de correspondências
  blockif = 0#blockif ajuda a discernir as aspas que iniciam e terminam
             #uma string

  chaves = ['class', 'else', 'false', 'fi', 'if', 'in', 'inherits', 'isvoid', 'let', 'loop', 'pool', 'then', 'while', 'case', 'esac', 'new', 'of', 'not', 'true']

  simbolos = ['[', ']', '{', '}', '(', ')', '.', ',', ';', ':', '<-', '~', '=>', '@']

  operators = ['+', '-', '*', '/', '=', '<', '>', '<=']

  commAndString = ['--', '(*', '*)', '""', '\"']
  
  regex = r"\"|\(\*|\*\)|\-\-|^class$|^else$|^false$|^fi$|^if$|^in$|^inherits$|^isvoid$|^let$|^loop$|^pool$|^then$|^while$|^case$|^esac$|^new$|^of$|^not$|^true$|\[|\]|\{|\}|\(|\)|\.|\,|\;|\:|\<\-|\<|\>|\+|\-|\=|\/|\*|^\d+$|^\w+$"
  
  
  p = re.compile(regex)#Compilar objeto de padrão regex
  match = p.search(word)#Retorna objeto Match
  if(match):
    corr = match.group(0)
    isInt = re.findall(r'^\d+\d$', corr)#Especificar Integer
    isTYPE = re.findall(r'^[A-Z]\w+$', corr)#Especificar TYPE ID
    isOBJ = re.findall(r'^[a-z]\w+$|^[a-z]?$', corr)#Especificar OBJ ID
    isKEY = 0;

    if(corr in commAndString):#Detecção de comentários e string
      if(corr == '--'):
        isCommentLine = 1
      elif(corr == '(*'):
        isCommentBlock = 1
      elif(corr == '*)'):
        isCommentBlock = 0
      elif(corr == '""'):
        matches.append((word, "string"))
      elif(corr == '"' and isString == 0 and blockif == 0 and isCommentLine == 0 and isCommentBlock == 0):
        isString = 1
        blockif = 1
        matches.append((word, "string"))
      elif(corr == '"' and isString == 1 and blockif == 0 and isCommentLine == 0 and isCommentBlock == 0):
        isString = 0
        blockif = 1

    #Ignorar correspondências caso ignore > 0
    ignore = isCommentBlock+isCommentLine+isString
    
    lowCorr = corr.lower()
    if(lowCorr in chaves and ignore == 0):#Detecção de palavras-chave
      matches.append((lowCorr, "keyword"))
      isKEY = 1;
      
    if(corr in simbolos and ignore == 0):#Detecção de símbolos
      if(corr == '['):
        matches.append((word, "sqBrackOpen"))
      elif(corr == ']'):
        matches.append((word, "sqBrackClose"))
      elif(corr == '{'):
        matches.append((word, "curBrackOpen"))
      elif(corr == '}'):
        matches.append((word, "curBrackClose"))
      elif(corr == '('):
        matches.append((word, "parenOpen"))
      elif(corr == ')'):
        matches.append((word, "parenClose"))
      elif(corr == '.'):
        matches.append((word, "dot"))
      elif(corr == ','):
        matches.append((word, "comma"))
      elif(corr == ';'):
        matches.append((word, "semiColon"))
      elif(corr == ':'):
        matches.append((word, "colon"))
      elif(corr == '<-'):
        matches.append((word, "atrib"))
      elif(corr == '\"'):
        matches.append((word, "quot"))
      elif(corr == '~'):
        matches.append((word, "til"))
      elif(corr == '=>'):
        matches.append((word, "arrow"))
      elif(corr == '@'):
        matches.append((word, "at"))

    if(isInt and ignore == 0):#Detecção de Integer
      matches.append((word, "INT"))
    
    if(isKEY == 0):    
      if(isTYPE and not isInt and not(corr in simbolos or corr in chaves 
         or corr in operators or corr in commAndString) and ignore == 0):
        matches.append((word, "TYPE"))#Detecção de TYPE
  
      if(isOBJ and not isInt and not(corr in simbolos or corr in chaves 
         or corr in operators or corr in commAndString) and ignore == 0):
        matches.append((word, "OBJ"))#Detecção de TYPE

    if(corr in operators and ignore == 0):#Detecção de operadores
      matches.append((word, "OP"))
  return matches, isCommentBlock, isCommentLine, isString
#Fim de função

#Tokenização
def tokenize(source):
  source = open(source, "r")
  lines = source.readlines()#Ler arquivo linha por linha e armazenar em lista
  
  tokens = []#Inicializar lista de tokens
  
  linecount = 0#Contagem de linhas
  commentBlockToggle = 0#Bloqueador bloco de comentário
  commentLineToggle = 0#Bloqueador linha de comentário
  stringToggle = 0#Bloqueador string
  
  for line in lines:#Para cada linha
    linecount += 1
    commentLineToggle = 0#Reiniciar bloqueador linha de comentário
    line = re.sub(r'(\({1}\*{1}|\(|\*{1}\){1}|\)|\[|\]|\{|\}|\/|\;|\:|\.|\>|\,|\<{1}\-{1}|\<|\+|\={1}\>{1}|\=|\-{1}\-{1}|\-|")', r' \1 ', str(line))#Adicionar whitespace entre símbolos
    words = re.split(r' ', line)#Separar linha em palavras
    for word in words:#Para cada palavra
      #Chamada checkword, retorna lista de tokens de correspondência
      #e estado de cada bloqueador
      matches, commentBlockToggle, commentLineToggle, stringToggle = checkword(word, commentBlockToggle, commentLineToggle, stringToggle)
      if matches:#Se houver alguma correnspondência
        for match in matches:
          tokens.append((match, linecount))#Adicionar tokens na lista
  
  #print("Lista de tokens:")
  #print(tokens)
  return tokens
#-----------------------------------------------------------


#-----------------------------------------------------------
#Análize Sintática
def printScope(scp):
#  if(scp == 1):
#    print("CLASS")
#  if(scp == 2):
#    print("FEATURE")
#  if(scp == 3):
#    print("FORMAL")
#  if(scp == 4):
#    print("EXPR")
#  if(scp == 5):
#    print("EXPR'")
  return
  
def nextToken(i, tokens):
  #print("From: ", i, tokens[i])
  if (i+1 < len(tokens)):
    #print("To: ", i+1, tokens[i+1])
    return (i+1, tokens[i+1])
  elif (i+1 >= len(tokens)):
    return 0

#EXPR'
def exprLeft(curToken, tokens):# A’ → αA / ∈
  printScope(5)
  if (curToken[1][0][1] == "OP"):#expr operador expr
    curToken = nextToken(curToken[0], tokens)
    curToken = exprCase(curToken, tokens)

  #expr[@TYPE].ID( [ expr [[, expr]]∗ ] )
  elif (curToken[1][0][1] == "at" or curToken[1][0][1] == "dot"):
    if (curToken[1][0][1] == "at"):
      curToken = nextToken(curToken[0], tokens)
      if (curToken[1][0][1] == "TYPE"):
        curToken = nextToken(curToken[0], tokens)
      else:
        print("Erro! Esperado -TYPE- após -@-", "\nLinha: ", curToken[1][1])
        quit()
        
    if (curToken[1][0][1] == "dot"):
      curToken = nextToken(curToken[0], tokens)
      if (curToken[1][0][1] == "OBJ"):
        curToken = nextToken(curToken[0], tokens)
      else:
        print("Erro! Esperado -ID- após - . -", "\nLinha: ", curToken[1][1])
        quit()
      if (curToken[1][0][1] == "parenOpen"):
        curToken = nextToken(curToken[0], tokens)
        if (curToken[1][0][1] == "parenClose"):
          curToken = nextToken(curToken[0], tokens)
          curToken = exprLeft(curToken, tokens)
          return curToken
        else:
          limit = 1
          x = 0
          while x < limit:
            curToken = exprLeft(curToken, tokens)
            curToken = exprCase(curToken, tokens)
            if (curToken[1][0][1] == "comma"):
              curToken = nextToken(curToken[0], tokens)
              limit+=1
            x+=1
        curToken = exprLeft(curToken, tokens)
        if (curToken[1][0][1] == "parenClose"):
          curToken = nextToken(curToken[0], tokens)
          curToken = exprLeft(curToken, tokens)
        else:
          print("Erro! Esperado -)-", "\nLinha: ", curToken[1][1])
          quit()
        return curToken
    
  return curToken

#EXPR
def exprCase(curToken, tokens):# A -> βA’
  printScope(4)
  #Terminais
  if (curToken[1][0][0] == "false"):#false
    curToken = nextToken(curToken[0], tokens)
    curToken = exprLeft(curToken, tokens)
    return curToken
  elif (curToken[1][0][0] == "true"):#true
    curToken = nextToken(curToken[0], tokens)
    curToken = exprLeft(curToken, tokens)
    return curToken
  elif (curToken[1][0][1] == "INT"):#integer
    curToken = nextToken(curToken[0], tokens)
    curToken = exprLeft(curToken, tokens)
    return curToken
  elif (curToken[1][0][1] == "string"):#string
    curToken = nextToken(curToken[0], tokens)
    curToken = exprLeft(curToken, tokens)
    return curToken
  elif (curToken[1][0][0] == "new"):#new TYPE
    curToken = nextToken(curToken[0], tokens)
    if (curToken[1][0][1] == "TYPE"):
      curToken = nextToken(curToken[0], tokens)
      curToken = exprLeft(curToken, tokens)
    else:
      print("Erro! Esperado -TYPE- após -new-", "\nLinha: ", curToken[1][1])
      quit()
    return curToken

  #ID
  elif (curToken[1][0][1] == "OBJ"):
    curToken = nextToken(curToken[0], tokens)
    if (curToken[1][0][1] == "atrib"):#ID <- expr
      curToken = nextToken(curToken[0], tokens)
      curToken = exprLeft(curToken, tokens)
      curToken = exprCase(curToken, tokens)
    elif (curToken[1][0][1] == "parenOpen"):#ID([expr[[,expr]]∗])
      curToken = nextToken(curToken[0], tokens)
      if (curToken[1][0][1] == "parenClose"):
        curToken = nextToken(curToken[0], tokens)
        return curToken
      else:
        limit = 1
        x = 0
        while x < limit:
          curToken = exprLeft(curToken, tokens)
          curToken = exprCase(curToken, tokens)
          if (curToken[1][0][1] == "comma"):
            curToken = nextToken(curToken[0], tokens)
            limit+=1
          x+=1
      curToken = exprLeft(curToken, tokens)
      if (curToken[1][0][1] == "parenClose"):
        curToken = nextToken(curToken[0], tokens)
        return curToken
      else:
        print("Erro! Esperado -)-", "\nLinha: ", curToken[1][1])
        quit()
    else:#ID terminal
      curToken = exprLeft(curToken, tokens)
    return curToken

  #Não terminais
  elif (curToken[1][0][1] == "isvoid"):#isvoid expr
    curToken = nextToken(curToken[0], tokens)
    curToken = exprLeft(curToken, tokens)
    curToken = exprCase(curToken, tokens)

  elif (curToken[1][0][0] == "not"):#not expr
    curToken = nextToken(curToken[0], tokens)
    curToken = exprLeft(curToken, tokens)
    curToken = exprCase(curToken, tokens)

  elif (curToken[1][0][1] == "til"):#˜expr
    curToken = nextToken(curToken[0], tokens)
    curToken = exprLeft(curToken, tokens)
    curToken = exprCase(curToken, tokens)

  elif (curToken[1][0][1] == "parenOpen"):#(expr)
    curToken = nextToken(curToken[0], tokens)
    curToken = exprCase(curToken, tokens)
    if (curToken[1][0][1] == "parenClose"):
      curToken = nextToken(curToken[0], tokens)
      return curToken
    else:
      print("Erro! Necessário fechar parênteses", "\nLinha: ", curToken[1][1])
      quit()

  elif (curToken[1][0][0] == "if"):#if then else fi
    curToken = nextToken(curToken[0], tokens)
    curToken = exprLeft(curToken, tokens)
    curToken = exprCase(curToken, tokens)
    if (curToken[1][0][0] == "then"):
      curToken = nextToken(curToken[0], tokens)
      curToken = exprLeft(curToken, tokens)
      curToken = exprCase(curToken, tokens)
    else:
      print("Erro! Esperado -then-", "\nLinha: ", curToken[1][1])
      quit()
    if (curToken[1][0][0] == "else"):
      curToken = nextToken(curToken[0], tokens)
      curToken = exprLeft(curToken, tokens)
      curToken = exprCase(curToken, tokens)
    else:
      print("Erro! Esperado -else-", "\nLinha: ", curToken[1][1])
      quit()
    if (curToken[1][0][0] == "fi"):
      curToken = nextToken(curToken[0], tokens)
    else:
      print("Erro! Esperado -fi-", "\nLinha: ", curToken[1][1])
      quit()

  elif (curToken[1][0][0] == "while"):#while loop pool
    curToken = nextToken(curToken[0], tokens)
    curToken = exprLeft(curToken, tokens)
    curToken = exprCase(curToken, tokens)
    if (curToken[1][0][0] == "loop"):
      curToken = nextToken(curToken[0], tokens)
      curToken = exprLeft(curToken, tokens)
      curToken = exprCase(curToken, tokens)
    else:
      print("Erro! Esperado -loop-", "\nLinha: ", curToken[1][1])
      quit()
    if (curToken[1][0][0] == "pool"):
      curToken = nextToken(curToken[0], tokens)
    else:
      print("Erro! Esperado -pool-", "\nLinha: ", curToken[1][1])
      quit()

  if (curToken[1][0][1] == "curBrackOpen"):#{ [[expr; ]]+}
    curToken = nextToken(curToken[0], tokens)
    curToken = exprLeft(curToken, tokens)
    curToken = exprCase(curToken, tokens)
    if (curToken[1][0][1] == "semiColon"):
      limit = 1
      x = 0
      while x < limit:
        curToken = exprLeft(curToken, tokens)
        curToken = exprCase(curToken, tokens)
        if (curToken[1][0][1] == "semiColon"):
          curToken = nextToken(curToken[0], tokens)
          limit+=1
        x+=1
    else:
      print("Erro! Esperado -;-", "\nLinha: ", curToken[1][1])
      quit()
    if (curToken[1][0][1] == "curBrackClose"):
      curToken = nextToken(curToken[0], tokens)
    else:
      print("Erro! Esperado -}-", "\nLinha: ", curToken[1][1])
      quit()

  if (curToken[1][0][0] == "let"):#let ID : TYPE in expr
    curToken = nextToken(curToken[0], tokens)
    if (curToken[1][0][1] == "OBJ"):
      curToken = nextToken(curToken[0], tokens)
    else:
      print("Erro! Esperado -ID- após -let-", "\nLinha: ", curToken[1][1])
      quit()
    if (curToken[1][0][1] == "colon"):
      curToken = nextToken(curToken[0], tokens)
    else:
      print("Erro! Esperado -:- após -ID-", "\nLinha: ", curToken[1][1])
      quit()
    if (curToken[1][0][1] == "TYPE"):
      curToken = nextToken(curToken[0], tokens)
    else:
      print("Erro! Esperado -TYPE- após -:-", "\nLinha: ", curToken[1][1])
      quit()

    if (curToken[1][0][1] == "atrib"):
      curToken = nextToken(curToken[0], tokens)
      curToken = exprLeft(curToken, tokens)
      curToken = exprCase(curToken, tokens)

    if (curToken[1][0][1] == "comma"):
      curToken = nextToken(curToken[0], tokens)
      if (curToken[1][0][1] == "OBJ"):
        curToken = nextToken(curToken[0], tokens)
      else:
        print("Erro! Esperado -ID-", "\nLinha: ", curToken[1][1])
        quit()
      if (curToken[1][0][1] == "colon"):
        curToken = nextToken(curToken[0], tokens)
      else:
        print("Erro! Esperado -:- após -ID-", "\nLinha: ", curToken[1][1])
        quit()
      if (curToken[1][0][1] == "TYPE"):
        curToken = nextToken(curToken[0], tokens)
      else:
        print("Erro! Esperado -TYPE- após -:-", "\nLinha: ", curToken[1][1])
        quit()
      if (curToken[1][0][1] == "atrib"):
        curToken = nextToken(curToken[0], tokens)
        curToken = exprLeft(curToken, tokens)
        curToken = exprCase(curToken, tokens)

    if (curToken[1][0][0] == "in"):
      curToken = nextToken(curToken[0], tokens)
      curToken = exprLeft(curToken, tokens)
      curToken = exprCase(curToken, tokens)
    else:
      print("Erro! Esperado -in-", "\nLinha: ", curToken[1][1])
      quit()

  if (curToken[1][0][0] == "case"):# case of esac
    curToken = nextToken(curToken[0], tokens)
    curToken = exprLeft(curToken, tokens)
    curToken = exprCase(curToken, tokens)
    if (curToken[1][0][0] == "of"):
      curToken = nextToken(curToken[0], tokens)
      limit = 1
      x = 0
      while x < limit:
        if (tokens[curToken[0]][0][0] != "esac"):
          if (curToken[1][0][1] == "OBJ"):#[[ID : TYPE => expr;]]+
            curToken = nextToken(curToken[0], tokens)
            if (curToken[1][0][1] == "colon"):
              curToken = nextToken(curToken[0], tokens)
            else:
              print("Erro! Esperado -:- após -ID-", "\nLinha: ", curToken[1][1])
              quit()
            if (curToken[1][0][1] == "TYPE"):
              curToken = nextToken(curToken[0], tokens)
            else:
              print("Erro! Esperado -TYPE- após -:-", "\nLinha: ", curToken[1][1])
              quit()
            if (curToken[1][0][0] == "=>"):
              curToken = nextToken(curToken[0], tokens)
              curToken = exprLeft(curToken, tokens)
              curToken = exprCase(curToken, tokens)
            else:
              print("Erro! Esperado - => - após -TYPE-", "\nLinha: ", curToken[1][1])
              quit()
          else:
            print("Erro! Esperado -ID- após -of-", "\nLinha: ", curToken[1][1])
            quit()
          if (curToken[1][0][1] == "semiColon"):
            curToken = nextToken(curToken[0], tokens)
            limit+=1
          else:
            print("Erro! Esperado -;- após -ID-", "\nLinha: ", curToken[1][1])
            quit()
        x+=1
    else:
      print("Erro! Esperado -of-", "\nLinha: ", curToken[1][1])
      quit()
    if (curToken[1][0][0] == "esac"):
      curToken = nextToken(curToken[0], tokens)
    else:
      print("Erro! Esperado -esac-", "\nLinha: ", curToken[1][1])
      quit()
  
  return curToken

#FORMAL
def formalCase(curToken, tokens):
  printScope(3)
  if (curToken == 0):
    return 0

  if (curToken[1][0][1] == "OBJ"):
    curToken = nextToken(curToken[0], tokens)
  else:
    curToken = nextToken(curToken[0], tokens)
    print("Erro! *formal* deve ser iniciado com -ID-", "\nLinha: ", curToken[1][1])
    quit()
    
  if (curToken[1][0][1] == "colon"):
    curToken = nextToken(curToken[0], tokens)
  else:
    curToken = nextToken(curToken[0], tokens)
    print("Erro! Esperado -:- após -ID-", "\nLinha: ", curToken[1][1])
    quit()
    
  if (curToken[1][0][1] == "TYPE"):
    curToken = nextToken(curToken[0], tokens)
  else:
    curToken = nextToken(curToken[0], tokens)
    print("Erro! Esperado -TYPE- após -:-", "\nLinha: ", curToken[1][1])
    quit()
        
  return curToken

#FEATURE
def featureCase(curToken, tokens):
  printScope(2)
  if (curToken == 0):
    return 0

  if (curToken[1][0][1] == "OBJ"):
    curToken = nextToken(curToken[0], tokens)
    if (curToken[1][0][1] == "parenOpen"):
      curToken = nextToken(curToken[0], tokens)
      if (curToken[1][0][1] != "parenClose"):
        curToken = formalCase(curToken, tokens)

      elif (curToken[1][0][1] == "comma"):
        limit = 1
        x = 0
        while x < limit:
          curToken = formalCase(curToken, tokens)
          if (curToken[1][0][1] == "comma"):
            curToken = nextToken(curToken[0], tokens)
            limit+=1
          x+=1

      if (curToken[1][0][1] == "parenClose"):
        curToken = nextToken(curToken[0], tokens)
        
        if (curToken[1][0][1] == "colon"):
          curToken = nextToken(curToken[0], tokens)
        else:
          print("Erro! Esperado -:-", "\nLinha: ", curToken[1][1])
          quit()
            
        if (curToken[1][0][1] == "TYPE"):
          curToken = nextToken(curToken[0], tokens)
        else:
          print("Erro! Esperado -TYPE-", "\nLinha: ", curToken[1][1])
          quit()

        if (curToken[1][0][1] == "curBrackOpen"):
          curToken = nextToken(curToken[0], tokens)
          curToken = exprCase(curToken, tokens)
        else:
          print("Erro! Esperado -{-", "\nLinha: ", curToken[1][1])
          quit()
          
        if (curToken[1][0][1] == "curBrackClose"):
          curToken = nextToken(curToken[0], tokens)
          return curToken
        else:
          print("Erro! Esperado -}-", "\nLinha: ", curToken[1][1])
          quit()
          
      else:
        print("Erro! Esperado -)-", "\nLinha: ", curToken[1][1])
        quit()
      
    elif (curToken[1][0][1] == "colon"):
      curToken = nextToken(curToken[0], tokens)
      
      if (curToken[1][0][1] == "TYPE"):
        curToken = nextToken(curToken[0], tokens)
      else:
        print("Erro! Esperado -TYPE-", "\nLinha: ", curToken[1][1])
        quit()
        
      if (curToken[1][0][1] == "atrib"):
        curToken = nextToken(curToken[0], tokens)
        curToken = exprLeft(curToken, tokens)
        curToken = exprCase(curToken, tokens)

    else:
      print("Erro! Esperado -(- ou -:- após ID", "\nLinha: ", curToken[1][1])
      quit()
      
  else:
    print("Erro! Feature deve iniciar com objeto ID", "\nLinha: ", curToken[1][1])
    quit()

  curToken = exprLeft(curToken, tokens)
  return curToken

#CLASS
def classCase(curToken, tokens):
  printScope(1)
  if (curToken == 0):
    return 0

  if (curToken[1][0][1] == "TYPE"):
    curToken = nextToken(curToken[0], tokens)
  else:
    print("Erro! Esperado objeto -TYPE- após -class-", "\nLinha: ", curToken[1][1])
    quit()
    
  if (curToken[1][0][0] == "inherits"):
    curToken = nextToken(curToken[0], tokens)
    if (curToken[1][0][1] == "TYPE"):
      curToken = nextToken(curToken[0], tokens)
    else:
      print("Erro! Esperado objeto -TYPE- após -inherits-", "\nLinha: ", curToken[1][1])
      quit()

  if (curToken[1][0][1] == "curBrackOpen"):
    curToken = nextToken(curToken[0], tokens)
    if (curToken[1][0][1] == "curBrackClose"):
      curToken = nextToken(curToken[0], tokens)
      return
    else:
      limit = 1
      x = 0
      while x < limit:
        curToken = featureCase(curToken, tokens)
        if(curToken[1][0][1] == "semiColon"):
          if (tokens[curToken[0]+1][0][1] != "curBrackClose"):
            curToken = nextToken(curToken[0], tokens)
            limit+=1
          else:
            break
        x+=1
      if(curToken[1][0][1] == "semiColon"):
        curToken = nextToken(curToken[0], tokens)
      else:
        print("Erro! Esperado -;-", "\nLinha: ", curToken[1][1])
        quit()
        
  else:
    print("Erro! Esperado -{-", "\nLinha: ", curToken[1][1])
    quit()
    
  return curToken

#PROGRAM
def sintAnalize(curToken, tokens):
  if (curToken == 0):
    print("Validado.")
    return

  if(curToken[1][0][0] == "class"):
    curToken = nextToken(curToken[0], tokens)
    curToken = classCase(curToken, tokens)    
  else:
    if(curToken[0] == 0):
      print("Erro! Esperado -class-", "\nLinha: ", curToken[1][1])
      quit()

  curToken = nextToken(curToken[0], tokens)
  sintAnalize(curToken, tokens)

#-----------------------------------------------------------


#source = open(sys.argv[1], "r")
#tokens = tokenize(source)
tokens = tokenize("sourcecode.cl")

curToken = (0, tokens[0])
sintAnalize(curToken, tokens)
