import re
import sys

#classe nó (Árvore)
class Node:
  type = None
  content = None
  pai = None
  filhos = []

#----------------------------------------------------------------------------------#

#classes método, classe, escopo e tipo
class Method:
  name = ""
  argumentTypes = []
  type = ""
  def __init__(self, n, a, t):
    self.name = n
    self.argumentTypes = a
    self.type = t
  
class Classe:
  name = ""
  methods = []
  def __init__(self, n):
    self.name = n

class Scope:
  upper = None
  IDs = []
  def __init__(self, u):
    self.upper = u

#Palavras reservadas
reserved = ['self', 'SELF_TYPE', 'class', 'else', 'false', 'fi', 'if', 'in', 'inherits', 'isvoid', 'let', 'loop', 'pool', 'then', 'while', 'case', 'esac', 'new', 'of', 'not', 'true']

#Adição de classes e métodos nativos de Cool
selftype = Classe("SELF_TYPE")

objeto = Classe("Object") #Object
objeto.methods.append(Method("abort", [], "Object"))
objeto.methods.append(Method("type_name", [], "String"))
objeto.methods.append(Method("copy", [], "SELF_TYPE"))

InOut = Classe("IO") #IO
InOut.methods.append(Method("out_string", ["String"], "SELF_TYPE"))
InOut.methods.append(Method("out_int", ["Int"], "SELF_TYPE"))
InOut.methods.append(Method("in_string", [], "String"))
InOut.methods.append(Method("in_int", [], "Int"))

Integer = Classe("Int") #Int

String = Classe("String") #String
String.methods.append(Method("length", [], "Int"))
String.methods.append(Method("concat", "String", "String"))
String.methods.append(Method("substr", ["Int", "Int"], "String"))

Boolean = Classe("Bool") #Bool

#Inicializar lista de tipos
classes = [selftype, objeto, InOut, Integer, String]

#Inicializar raíz do escopo
scopeRoot = Scope(None)

#----------------------------------------------------------------------------------#

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

#Checagem de tipo e escopo
def checkScopeAndType(name, type, scope, equality, line): #type pode ser "class", "var" ou "method"
  global reserved
  global classes

  if (name == "self"):
    return

  for word in reserved:
    if (name == word and not equality):
      print("O nome ", name, " pertence a uma palavra reservada. Linha: ", line)
      quit()

  for word in classes:
    if (name == word and not equality):
      print("O nome ", name, " pertence a uma classe nativa. Utilize outro. Linha: ", line)
      quit()

  if (type == "class"):
    if (name == "Int" and not equality):
      print("O tipo -Int- não pode ser herdado nem redefinido. Linha: ", line)
      quit()
    if (name == "String" and not equality):
      print("O tipo -String- não pode ser herdado nem redefinido. Linha: ", line)
      quit()

  if (not equality):
    if (type == "class"):
      for c in classes:
        if (name == c.name):
          print("Classe ", name, " já existe. Linha: ", line)
          quit()
  
    if (type == "var"):
      for v in scope.IDs:
        if (name == v):
          print("Identificador ", name, " já existe. Linha: ", line)
          quit()

    if (type == "method"):
      for c in classes:
        for m in c.methods:
          if (name == m.name):
            print("Método ", name, " já existe. Linha: ", line)
            quit()

  if (equality):
    if (type == "class"):
      for c in classes:
        if (name == c.name):
          return
      print("Classe ", name, "não declarada. Linha: ", line)
      quit()

    if (type == "var"):
      for v in scope.IDs:
        if (name == v):
          return
      if (scope.upper != None): #Se o escopo estiver dentro de outro
        scopeCopy = scope.upper  #Armazenar escopo superior em variável temporária      
      loopToggle = 0
      while loopToggle == 0:
        for ID in scopeCopy.IDs:
          if (name == ID):
            return
        if (scopeCopy.upper != None):
          scopeCopy = scopeCopy.upper
        else:
          print("Identificador ", name, " não declarado. Linha: ", line)
          quit()

    if (type == "method"):
      for c in classes:
        for m in c.methods:
          if (name == m.name):
            return
          
  return
  
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
def exprLeft(curToken, tokens, pai, upperScope, classePai):# A’ → αA / ∈
  
  exprAtual = Node()
  exprAtual.type = "Expr"
  exprAtual.pai = pai

  escopoAtual = Scope(upperScope)
  
  printScope(5)
  if (curToken[1][0][1] == "OP"):#expr operador expr
    operator = Node()
    operator.type = "Operation"
    operator.content = curToken[1][0][0]
    operator.pai = exprAtual
    exprAtual.filhos.append(operator)
    curToken = nextToken(curToken[0], tokens)
    curToken = exprCase(curToken, tokens, exprAtual)
    pai.filhos.append(exprAtual)
    return curToken

  #expr[@TYPE].ID( [ expr [[, expr]]∗ ] )
  elif (curToken[1][0][1] == "at" or curToken[1][0][1] == "dot"):
    call = Node()
    call.type = "Method call"
    call.pai = exprAtual
    exprAtual.filhos.append(call)
    if (curToken[1][0][1] == "at"):
      curToken = nextToken(curToken[0], tokens)
      if (curToken[1][0][1] == "TYPE"):
        type = Node()
        type.type = "TYPE"
        type.content = curToken[1][0][0]
        type.pai = exprAtual
        exprAtual.filhos.append(type)

        checkScopeAndType(curToken[1][0][0], "class", escopoAtual, True, curToken[1][1])
        
        curToken = nextToken(curToken[0], tokens)
      else:
        print("Erro! Esperado -TYPE- após -@-", "\nLinha: ", curToken[1][1])
        quit()
        
    if (curToken[1][0][1] == "dot"):
      curToken = nextToken(curToken[0], tokens)
      if (curToken[1][0][1] == "OBJ"):
        ID = Node()
        ID.type = "ID"
        ID.content = curToken[1][0][0]
        ID.pai = exprAtual
        exprAtual.filhos.append(ID)

        checkScopeAndType(curToken[1][0][0], "method", escopoAtual, True, curToken[1][1])
        
        curToken = nextToken(curToken[0], tokens)
      else:
        print("Erro! Esperado -ID- após - . -", "\nLinha: ", curToken[1][1])
        quit()
      if (curToken[1][0][1] == "parenOpen"):
        curToken = nextToken(curToken[0], tokens)
        if (curToken[1][0][1] == "parenClose"):
          curToken = nextToken(curToken[0], tokens)
          curToken = exprLeft(curToken, tokens, exprAtual, escopoAtual, classePai)

          pai.filhos.append(exprAtual)
          return curToken
        else:
          limit = 1
          x = 0
          while x < limit:
            curToken = exprLeft(curToken, tokens, exprAtual, escopoAtual, classePai)
            curToken = exprCase(curToken, tokens, exprAtual, escopoAtual, classePai)
            if (curToken[1][0][1] == "comma"):
              curToken = nextToken(curToken[0], tokens)
              limit+=1
            x+=1
        curToken = exprLeft(curToken, tokens, exprAtual, escopoAtual, classePai)
        if (curToken[1][0][1] == "parenClose"):
          curToken = nextToken(curToken[0], tokens)
          curToken = exprLeft(curToken, tokens, exprAtual, escopoAtual, classePai)
        else:
          print("Erro! Esperado -)-", "\nLinha: ", curToken[1][1])
          quit()

        pai.filhos.append(exprAtual)
        return curToken
        
  return curToken

#EXPR
def exprCase(curToken, tokens, pai, upperScope, classePai):# A -> βA’
  
  exprAtual = Node()
  exprAtual.type = "Expr"
  exprAtual.pai = pai

  escopoAtual = Scope(upperScope)
  
  printScope(4)
  #Terminais
  if (curToken[1][0][0] == "false"):#false
    bool = Node()
    bool.type = "Boolean"
    bool.content = curToken[1][0][0]
    bool.pai = exprAtual
    exprAtual.filhos.append(bool)
    curToken = nextToken(curToken[0], tokens)
    curToken = exprLeft(curToken, tokens, exprAtual, escopoAtual, classePai)
    pai.filhos.append(exprAtual)
    return curToken
  elif (curToken[1][0][0] == "true"):#true
    bool = Node()
    bool.type = "Boolean"
    bool.content = curToken[1][0][0]
    bool.pai = exprAtual
    exprAtual.filhos.append(bool)
    curToken = nextToken(curToken[0], tokens)
    curToken = exprLeft(curToken, tokens, exprAtual, escopoAtual, classePai)
    pai.filhos.append(exprAtual)
    return curToken
  elif (curToken[1][0][1] == "INT"):#integer
    int = Node()
    int.type = "integer"
    int.content = curToken[1][0][0]
    int.pai = exprAtual
    exprAtual.filhos.append(int)
    curToken = nextToken(curToken[0], tokens)
    curToken = exprLeft(curToken, tokens, exprAtual, escopoAtual, classePai)
    pai.filhos.append(exprAtual)
    return curToken
  elif (curToken[1][0][1] == "string"):#string
    string = Node()
    string.type = "string"
    string.content = curToken[1][0][0]
    string.pai = exprAtual
    exprAtual.filhos.append(string)
    curToken = nextToken(curToken[0], tokens)
    curToken = exprLeft(curToken, tokens, exprAtual, escopoAtual, classePai)
    pai.filhos.append(exprAtual)
    return curToken
  elif (curToken[1][0][0] == "new"):#new TYPE
    exprAtual.type = "Class instantiation"
    curToken = nextToken(curToken[0], tokens)
    if (curToken[1][0][1] == "TYPE"):
      type = Node()
      type.type = "Type"
      type.content = curToken[1][0][0]
      type.pai = exprAtual
      exprAtual.filhos.append(type)

      checkScopeAndType(curToken[1][0][0], "class", escopoAtual, True, curToken[1][1])
      
      curToken = nextToken(curToken[0], tokens)
      curToken = exprLeft(curToken, tokens, exprAtual, escopoAtual, classePai)
    else:
      print("Erro! Esperado -TYPE- após -new-", "\nLinha: ", curToken[1][1])
      quit()
    pai.filhos.append(exprAtual)
    return curToken

  #ID
  elif (curToken[1][0][1] == "OBJ"):
    ID = Node()
    ID.type = "ID"
    ID.content = curToken[1][0][0]
    ID.pai = exprAtual
    exprAtual.filhos.append(ID)

    if (nextToken(curToken[0], tokens)[1][0][1] == "parenOpen"):
      checkScopeAndType(curToken[1][0][0], "method", escopoAtual, True, curToken[1][1])
    else:
      checkScopeAndType(curToken[1][0][0], "var", escopoAtual, True, curToken[1][1])      
    
    curToken = nextToken(curToken[0], tokens)
    if (curToken[1][0][1] == "atrib"):#ID <- expr
      atrib = Node()
      atrib.type = "Atribuition to ID"
      atrib.pai = exprAtual
      exprAtual.filhos.append(atrib)
      curToken = nextToken(curToken[0], tokens)
      curToken = exprLeft(curToken, tokens, exprAtual, escopoAtual, classePai)
      curToken = exprCase(curToken, tokens, exprAtual, escopoAtual, classePai)
    elif (curToken[1][0][1] == "parenOpen"):#ID([expr[[,expr]]∗])
      curToken = nextToken(curToken[0], tokens)
      if (curToken[1][0][1] == "parenClose"):
        curToken = nextToken(curToken[0], tokens)
        pai.filhos.append(exprAtual)
        return curToken
      else:
        limit = 1
        x = 0
        while x < limit:
          curToken = exprLeft(curToken, tokens, exprAtual, escopoAtual, classePai)
          curToken = exprCase(curToken, tokens, exprAtual, escopoAtual, classePai)
          if (curToken[1][0][1] == "comma"):
            curToken = nextToken(curToken[0], tokens)
            limit+=1
          x+=1
      curToken = exprLeft(curToken, tokens, exprAtual, escopoAtual, classePai)
      if (curToken[1][0][1] == "parenClose"):
        curToken = nextToken(curToken[0], tokens)
        pai.filhos.append(exprAtual)
        return curToken
      else:
        print("Erro! Esperado -)-", "\nLinha: ", curToken[1][1])
        quit()
    else:#ID terminal
      ID = Node()
      ID.type = "Single ID"
      ID.content = curToken[1][0][0]
      ID.pai = exprAtual
      exprAtual.filhos.append(ID)
      curToken = exprLeft(curToken, tokens, exprAtual, escopoAtual, classePai)      
    pai.filhos.append(exprAtual)
    return curToken

  #Não terminais
  elif (curToken[1][0][1] == "isvoid"):#isvoid expr
    isvoid = Node()
    isvoid.type = "IsVoid"
    isvoid.content = curToken[1][0][0]
    isvoid.pai = exprAtual
    exprAtual.filhos.append(isvoid)
    curToken = nextToken(curToken[0], tokens)
    curToken = exprLeft(curToken, tokens, exprAtual, escopoAtual, classePai)
    curToken = exprCase(curToken, tokens, exprAtual, escopoAtual, classePai)

  elif (curToken[1][0][0] == "not"):#not expr
    negation = Node()
    negation.type = "IsVoid"
    negation.content = curToken[1][0][0]
    negation.pai = exprAtual
    exprAtual.filhos.append(negation)
    curToken = nextToken(curToken[0], tokens)
    curToken = exprLeft(curToken, tokens, exprAtual, escopoAtual, classePai)
    curToken = exprCase(curToken, tokens, exprAtual, escopoAtual, classePai)

  elif (curToken[1][0][1] == "til"):#˜expr
    til = Node()
    til.type = "Til(~)"
    til.content = curToken[1][0][0]
    til.pai = exprAtual
    exprAtual.filhos.append(til)
    curToken = nextToken(curToken[0], tokens)
    curToken = exprLeft(curToken, tokens, exprAtual, escopoAtual, classePai)
    curToken = exprCase(curToken, tokens, exprAtual, escopoAtual, classePai)

  elif (curToken[1][0][1] == "parenOpen"):#(expr)
    curToken = nextToken(curToken[0], tokens)
    curToken = exprCase(curToken, tokens, exprAtual, escopoAtual, classePai)
    if (curToken[1][0][1] == "parenClose"):
      curToken = nextToken(curToken[0], tokens)
      pai.filhos.append(exprAtual)
      return curToken
    else:
      print("Erro! Necessário fechar parênteses", "\nLinha: ", curToken[1][1])
      quit()

  elif (curToken[1][0][0] == "if"):#if then else fi
    if_statement = Node()
    if_statement.type = "if_statement"
    if_statement.pai = exprAtual
    exprAtual.filhos.append(if_statement)
    curToken = nextToken(curToken[0], tokens)
    curToken = exprLeft(curToken, tokens, exprAtual, escopoAtual, classePai)
    curToken = exprCase(curToken, tokens, exprAtual, escopoAtual, classePai)
    if (curToken[1][0][0] == "then"):
      then = Node()
      then.type = "then"
      then.pai = exprAtual
      exprAtual.filhos.append(then)
      curToken = nextToken(curToken[0], tokens)
      curToken = exprLeft(curToken, tokens, exprAtual, escopoAtual, classePai)
      curToken = exprCase(curToken, tokens, exprAtual, escopoAtual, classePai)
    else:
      print("Erro! Esperado -then-", "\nLinha: ", curToken[1][1])
      quit()
    if (curToken[1][0][0] == "else"):
      else_statement = Node()
      else_statement.type = "else_statement"
      else_statement.pai = exprAtual
      exprAtual.filhos.append(else_statement)
      curToken = nextToken(curToken[0], tokens)
      curToken = exprLeft(curToken, tokens, exprAtual, escopoAtual, classePai)
      curToken = exprCase(curToken, tokens, exprAtual, escopoAtual, classePai)
    else:
      print("Erro! Esperado -else-", "\nLinha: ", curToken[1][1])
      quit()
    if (curToken[1][0][0] == "fi"):
      fi = Node()
      fi.type = "endif"
      fi.pai = exprAtual
      exprAtual.filhos.append(fi)
      curToken = nextToken(curToken[0], tokens)
    else:
      print("Erro! Esperado -fi-", "\nLinha: ", curToken[1][1])
      quit()

  elif (curToken[1][0][0] == "while"):#while loop pool
    while_statement = Node()
    while_statement.type = "while_begin"
    while_statement.pai = exprAtual
    exprAtual.filhos.append(while_statement)
    curToken = nextToken(curToken[0], tokens)
    curToken = exprLeft(curToken, tokens, exprAtual, escopoAtual, classePai)
    curToken = exprCase(curToken, tokens, exprAtual, escopoAtual, classePai)
    if (curToken[1][0][0] == "loop"):
      loop = Node()
      loop.type = "loop_while"
      loop.pai = exprAtual
      exprAtual.filhos.append(loop)
      curToken = nextToken(curToken[0], tokens)
      curToken = exprLeft(curToken, tokens, exprAtual, escopoAtual, classePai)
      curToken = exprCase(curToken, tokens, exprAtual, escopoAtual, classePai)
    else:
      print("Erro! Esperado -loop-", "\nLinha: ", curToken[1][1])
      quit()
    if (curToken[1][0][0] == "pool"):
      pool = Node()
      pool.type = "end_loop"
      pool.pai = exprAtual
      exprAtual.filhos.append(pool)
      curToken = nextToken(curToken[0], tokens)
    else:
      print("Erro! Esperado -pool-", "\nLinha: ", curToken[1][1])
      quit()

  if (curToken[1][0][1] == "curBrackOpen"):#{ [[expr; ]]+}
    parameter = Node()
    parameter.type = "Parameters"
    parameter.pai = exprAtual
    exprAtual.filhos.append(parameter)
    curToken = nextToken(curToken[0], tokens)
    curToken = exprLeft(curToken, tokens, exprAtual, escopoAtual, classePai)
    curToken = exprCase(curToken, tokens, exprAtual, escopoAtual, classePai)
    if (curToken[1][0][1] == "semiColon"):
      limit = 1
      x = 0
      while x < limit:
        curToken = exprLeft(curToken, tokens, exprAtual, escopoAtual, classePai)
        curToken = exprCase(curToken, tokens, exprAtual, escopoAtual, classePai)
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
    let = Node()
    let.type = "let statement"
    let.pai = exprAtual
    exprAtual.filhos.append(let)
    curToken = nextToken(curToken[0], tokens)
    if (curToken[1][0][1] == "OBJ"):
      ID = Node()
      ID.type = "ID"
      ID.content = curToken[1][0][0]
      ID.pai = exprAtual
      exprAtual.filhos.append(ID)

      checkScopeAndType(curToken[1][0][0], "var", escopoAtual, False, curToken[1][1])
      
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
      TYPE = Node()
      TYPE.type = "Type"
      TYPE.content = curToken[1][0][0]
      TYPE.pai = exprAtual
      exprAtual.filhos.append(TYPE)

      checkScopeAndType(curToken[1][0][0], "class", escopoAtual, True, curToken[1][1])
      
      curToken = nextToken(curToken[0], tokens)
    else:
      print("Erro! Esperado -TYPE- após -:-", "\nLinha: ", curToken[1][1])
      quit()

    if (curToken[1][0][1] == "atrib"):
      atrib = Node()
      atrib.type = "Atribuition"
      atrib.pai = exprAtual
      exprAtual.filhos.append(atrib)
      curToken = nextToken(curToken[0], tokens)
      curToken = exprLeft(curToken, tokens, exprAtual, escopoAtual, classePai)
      curToken = exprCase(curToken, tokens, exprAtual, escopoAtual, classePai)

    if (curToken[1][0][1] == "comma"):
      curToken = nextToken(curToken[0], tokens)
      if (curToken[1][0][1] == "OBJ"):
        ID = Node()
        ID.type = "ID"
        ID.content = curToken[1][0][0]
        ID.pai = exprAtual
        exprAtual.filhos.append(ID)
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
        type = Node()
        type.type = "Type"
        type.content = curToken[1][0][0]
        type.pai = exprAtual
        exprAtual.filhos.append(type)
        curToken = nextToken(curToken[0], tokens)
      else:
        print("Erro! Esperado -TYPE- após -:-", "\nLinha: ", curToken[1][1])
        quit()
      if (curToken[1][0][1] == "atrib"):
        atrib = Node()
        atrib.type = "Atribuition"
        atrib.pai = exprAtual
        exprAtual.filhos.append(atrib)
        curToken = nextToken(curToken[0], tokens)
        curToken = exprLeft(curToken, tokens, exprAtual, escopoAtual, classePai)
        curToken = exprCase(curToken, tokens, exprAtual, escopoAtual, classePai)

    if (curToken[1][0][0] == "in"):
      curToken = nextToken(curToken[0], tokens)
      curToken = exprLeft(curToken, tokens, exprAtual, escopoAtual, classePai)
      curToken = exprCase(curToken, tokens, exprAtual, escopoAtual, classePai)
    else:
      print("Erro! Esperado -in-", "\nLinha: ", curToken[1][1])
      quit()

  if (curToken[1][0][0] == "case"):# case of esac
    case = Node()
    case.type = "case_statement"
    case.pai = exprAtual
    exprAtual.filhos.append(case)
    curToken = nextToken(curToken[0], tokens)
    curToken = exprLeft(curToken, tokens, exprAtual, escopoAtual, classePai)
    curToken = exprCase(curToken, tokens, exprAtual, escopoAtual, classePai)
    if (curToken[1][0][0] == "of"):
      of = Node()
      of.type = "case_options"
      of.pai = exprAtual
      exprAtual.filhos.append(of)
      curToken = nextToken(curToken[0], tokens)
      limit = 1
      x = 0
      while x < limit:
        if (tokens[curToken[0]][0][0] != "esac"):
          if (curToken[1][0][1] == "OBJ"):#[[ID : TYPE => expr;]]+
            ID = Node()
            ID.type = "ID"
            ID.content = curToken[1][0][0]
            ID.pai = exprAtual
            exprAtual.filhos.append(ID)
            curToken = nextToken(curToken[0], tokens)
            if (curToken[1][0][1] == "colon"):
              curToken = nextToken(curToken[0], tokens)
            else:
              print("Erro! Esperado -:- após -ID-", "\nLinha: ", curToken[1][1])
              quit()
            if (curToken[1][0][1] == "TYPE"):
              type = Node()
              type.type = "Type"
              type.content = curToken[1][0][0]
              type.pai = exprAtual
              exprAtual.filhos.append(type)

              checkScopeAndType(curToken[1][0][0], "class", escopoAtual, True, curToken[1][1])
              
              curToken = nextToken(curToken[0], tokens)
            else:
              print("Erro! Esperado -TYPE- após -:-", "\nLinha: ", curToken[1][1])
              quit()
            if (curToken[1][0][0] == "=>"):
              funcCall = Node()
              funcCall.type = "function_call"
              funcCall.pai = exprAtual
              exprAtual.filhos.append(funcCall)
              curToken = nextToken(curToken[0], tokens)
              curToken = exprLeft(curToken, tokens, exprAtual, escopoAtual, classePai)
              curToken = exprCase(curToken, tokens, exprAtual, escopoAtual, classePai)
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
      esac = Node()
      esac.type = "end_case"
      esac.pai = exprAtual
      exprAtual.filhos.append(esac)
      curToken = nextToken(curToken[0], tokens)
    else:
      print("Erro! Esperado -esac-", "\nLinha: ", curToken[1][1])
      quit()
  
  pai.filhos.append(exprAtual)
  return curToken

#FORMAL
def formalCase(curToken, tokens, pai, upperScope, classePai, method):
  global formalNodeList

  formalAtual = Node()
  formalAtual.type = "Formal"
  formalAtual.pai = pai
  
  escopoAtual = Scope(upperScope)
  
  printScope(3)
  if (curToken == 0):
    return 0

  if (curToken[1][0][1] == "OBJ"):
    ID = Node()
    ID.content = curToken[1][0][0]
    ID.pai = formalAtual
    formalAtual.filhos.append(ID)

    checkScopeAndType(curToken[1][0][0], "var", escopoAtual, False, curToken[1][1])
    escopoAtual.IDs.append(curToken[1][0][0])
    
    curToken = nextToken(curToken[0], tokens)
  else:
    print("Erro! *formal* deve ser iniciado com -ID-", "\nLinha: ", curToken[1][1])
    quit()
    
  if (curToken[1][0][1] == "colon"):
    curToken = nextToken(curToken[0], tokens)
  else:
    print("Erro! Esperado -:- após -ID-", "\nLinha: ", curToken[1][1])
    quit()
    
  if (curToken[1][0][1] == "TYPE"):
    type = Node()
    type.content = curToken[1][0][0]
    type.pai = formalAtual
    formalAtual.filhos.append(type)

    checkScopeAndType(curToken[1][0][0], "class", escopoAtual, True, curToken[1][1])
    method.argumentTypes.append(curToken[1][0][0])
    
    curToken = nextToken(curToken[0], tokens)
  else:
    print("Erro! Esperado -TYPE- após -:-", "\nLinha: ", curToken[1][1])
    quit()
        
  pai.filhos.append(formalAtual)
  return curToken

#FEATURE
def featureCase(curToken, tokens, pai, upperScope, classePai): 

  featureAtual = Node()
  featureAtual.type = "Feature"
  featureAtual.pai = pai

  escopoAtual = Scope(upperScope)
  
  printScope(2)
  if (curToken == 0):
    return 0

  if (curToken[1][0][1] == "OBJ"):
    ID = Node()
    ID.content = curToken[1][0][0]
    ID.pai = featureAtual
    featureAtual.filhos.append(ID)

    tempMethod = Method(None, [], None)

    if (nextToken(curToken[0] + 1, tokens)[1][0][1] == "TYPE"):
      checkScopeAndType(curToken[1][0][0], "var", escopoAtual, False, curToken[1][1])
      escopoAtual.IDs.append(curToken[1][0][0])
    else:
      checkScopeAndType(curToken[1][0][0], "var", escopoAtual, False, curToken[1][1])
      tempMethod.name = curToken[1][0][0]
      
    curToken = nextToken(curToken[0], tokens)
    if (curToken[1][0][1] == "parenOpen"):
      curToken = nextToken(curToken[0], tokens)
      if (curToken[1][0][1] != "parenClose"):
        curToken = formalCase(curToken, tokens, featureAtual, escopoAtual, classePai, tempMethod)

      elif (curToken[1][0][1] == "comma"):
        limit = 1
        x = 0
        while x < limit:
          curToken = formalCase(curToken, tokens, featureAtual, escopoAtual, classePai, tempMethod)
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
          type = Node()
          type.content = curToken[1][0][0]
          type.pai = featureAtual
          featureAtual.filhos.append(type)

          checkScopeAndType(curToken[1][0][0], "class", escopoAtual, True, curToken[1][1])
          tempMethod.type = curToken[1][0][0]
          classePai.methods.append(tempMethod)
          
          curToken = nextToken(curToken[0], tokens)
        else:
          print("Erro! Esperado -TYPE-", "\nLinha: ", curToken[1][1])
          quit()

        if (curToken[1][0][1] == "curBrackOpen"):
          curToken = nextToken(curToken[0], tokens)
          curToken = exprCase(curToken, tokens, featureAtual, escopoAtual, classePai)
          
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
        type = Node()
        type.content = curToken[1][0][0]
        type.pai = featureAtual
        featureAtual.filhos.append(type)

        checkScopeAndType(curToken[1][0][0], "class", escopoAtual, True, curToken[1][1])
        
        curToken = nextToken(curToken[0], tokens)
      else:
        print("Erro! Esperado -TYPE-", "\nLinha: ", curToken[1][1])
        quit()
        
      if (curToken[1][0][1] == "atrib"):
        curToken = nextToken(curToken[0], tokens)
        curToken = exprLeft(curToken, tokens, featureAtual, escopoAtual, classePai)
        curToken = exprCase(curToken, tokens, featureAtual, escopoAtual, classePai)

    else:
      print("Erro! Esperado -(- ou -:- após ID", "\nLinha: ", curToken[1][1])
      quit()
      
  else:
    print("Erro! Feature deve iniciar com objeto ID", "\nLinha: ", curToken[1][1])
    quit()

  curToken = exprLeft(curToken, tokens, featureAtual, escopoAtual, classePai)
  pai.filhos.append(featureAtual)
  return curToken

#CLASS
def classCase(curToken, tokens, pai, upperScope, classePai):

  classeAtual = Node()
  classeAtual.type = "Class"

  escopoAtual = Scope(upperScope)
  
  printScope(1)
  if (curToken == 0):
    return 0

  if (curToken[1][0][1] == "TYPE"):
    classTYPE = Node()
    classTYPE.content = curToken[1][0][0]
    classTYPE.pai = classeAtual
    classeAtual.filhos.append(classTYPE)
    curToken = nextToken(curToken[0], tokens)
  else:
    print("Erro! Esperado objeto -TYPE- após -class-", "\nLinha: ", curToken[1][1])
    quit()
    
  if (curToken[1][0][0] == "inherits"):
    curToken = nextToken(curToken[0], tokens)
    if (curToken[1][0][1] == "TYPE"):
      inheritsTYPE = Node()
      inheritsTYPE.content = curToken[1][0][0]
      inheritsTYPE.pai = classeAtual
      classeAtual.filhos.append(inheritsTYPE)

      checkScopeAndType(curToken[1][0][0], "class", escopoAtual, True, curToken[1][1])
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
        curToken = featureCase(curToken, tokens, classeAtual, escopoAtual, classePai)
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
    
  pai.filhos.append(classeAtual)    
  return curToken

#PROGRAM
def sintAnalize(curToken, tokens, rootNode):
  global scopeRoot
  global classes
  
  if (curToken == 0):
    print("Validado.")
    return

  if(curToken[1][0][0] == "class"):
    curToken = nextToken(curToken[0], tokens)
    checkScopeAndType(curToken[1][0][0], "class", scopeRoot, False, curToken[1][1])
    tempClass = Classe(curToken[1][0][0])
    curToken = classCase(curToken, tokens, rootNode, scopeRoot, tempClass)
    classes.append(tempClass)
  else:
    if(curToken[0] == 0):
      print("Erro! Esperado -class-", "\nLinha: ", curToken[1][1])
      quit()

  curToken = nextToken(curToken[0], tokens)
  sintAnalize(curToken, tokens, rootNode)

#-----------------------------------------------------------


#source = open(sys.argv[1], "r")
#tokens = tokenize(source)
tokens = tokenize("sourcecode.cl")

semanticTree = Node()
semanticTree.type = "Root"

curToken = (0, tokens[0])
sintAnalize(curToken, tokens, semanticTree)

for c in classes:
  print(c.name)