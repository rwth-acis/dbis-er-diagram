# Installation
```python
pip install dbis-er-diagram
```
# Einführung in das Entity-Relationship-Modell, ER-Malwerkzeug
In der Vorlesung haben Sie das Relationale Datenmodell kennengelernt. ER-Diagramme bieten ein Modell zur Darstellung von Entitäten und deren Relationen.

Dieses Blatt gibt einen kurzen Überblick über die Elemente des Entity-Relationship-Modells (ER-Modell) und eine Einführung in ein von uns entwickeltes Python-tool, welches euch das digitale Zeichnen von ER-Diagrammen erleichtern soll. 

Die folgende Zelle importiert das Python Modul und ermöglicht dessen Nutzung innerhalb des Notebooks:
```python
from erdiagram.ER import ER
```
Diese Zeile muss einmalig am Anfang des Notebooks ausgeführt werden.

## Entities
> Neue Entität zum Graphen hinzufügen: `add_node()`

**Entities** sind Objekte - konkrete oder abstrakte Gegenstände oder Wesen, welche sich von anderen Entities unterscheiden. Beispiele hierfür sind *Person, Auto, Kunde, Buch, etc.*  
**Entity-Typen** sind Mengen von Entities, welche die gleichen Attribute besitzen. Beispiele für Entity-Typen sind *Personen, Autos, Kunden, etc.*  
Entity-Typen werden in ER-Diagrammen durch Rechtecke dargestellt.  
Der Befehl um einen Entity-Typen zum Diagramm hinzuzufügen ist ```add_node("Entity Name")```

``` python .noeval
add_node(label, isMultiple = False, isWeak = False)
``` 

#### Funktionsparameter
- `label(str)`: Knotenbezeichnung
- `isMultiple(bool)`: Ist die Kardinalität des Knotens mehrfach oder singulär?
- `isWeak(bool)`: Ist dies ein schwacher Knoten?

#### Beispiel
``` python
# Initialisiere ein neues ER-Diagramm und speichere die Referenz in der Variable g
g = ER()

# Füge einen neuen Knoten mit dem Namen Buch hinzu
g.add_node("Buch")

# Zeichne das Diagramm
g.display()
``` 


---


## Attribute und Schlüssel
> Neues Attribut zu einer Entität im Graphen hinzufügen `add_attribute()`

Alle Mitglieder eines Entity-Typs werden durch eine Menge charakterisierender **Eigenschaften (Attributes)** beschrieben. Beispiele hierfür sind *Farbe, Gewicht und Preis* beim Entity-Typ *Teile*.  Die Werte eines Attributes stammen normalerweise aus Wertebereichen wie ```INTEGER```, ```REAL```, ```STRING```, etc. aber auch strukturierte Werte wie Listen, Bäume, usw. sind vorstellbar.  

Ein **Schlüssel** ist eine minimale Menge von Attributen, deren Werte das zugeordnete Entity eindeutig innerhalb aller Entities seines Typs identifiziert.  
Attribute werden im ER-Diagramm durch Ellipsen dargestellt:
- Attribute sind über ungerichtete Kanten mit dem zugehörigen Entity-Typ verbunden.
- Schlüssel-Attribute (_primary key_) werden (in der Regel) unterstrichen.

Der Befehl um ein Attribut zu einem Entity-Typen hinzuzufügen ist ```add_attribute("Entity-Type name", "Attribute name")```.  
Um ein Attribut als Schlüssel-Attribut zu kennzeichnen, muss außerdem der Parameter ```isPK``` auf ```True``` gesetzt werden.

``` python .noeval
g.add_attribute( nodeLabel, attrLabel,
                 isPK = False, isMultiple = False,
                 isWeak = False, composedOf=[])
``` 

#### Funktionsparameter
- `nodeLabel(str)`: Bezeichnung des übergeordneten Knotens
- `attrLabel(str)`: Bezeichnung des Attributs
- `isPK(bool)`: Ist dieses Attribut der Primärschlüssel?
- `isMultiple(bool)`: Ist die Kardinalität des Knotens mehrfach oder singulär?
- `isWeak(bool)`: Ist dies ein schwaches Attribut?
- `composedOf(list)`: Liste der Attribute, aus denen sich dieses Attribut zusammensetzt

#### Beispiel
``` python
g = ER()
g.add_node("Buch")

# Attribute hinzufügen
g.add_attribute("Buch", "Titel")
g.add_attribute("Buch", "Seitenanzahl")

# Die ISBN beschreibt ein Buch eindeutig und ist daher ein Schlüssel-Attribut
g.add_attribute("Buch", "ISBN", isPK=True)
g.display()
``` 


---


### Zusammengesetzte Attribute

Ein Attribut kann aus anderen Attributen bestehen. Ein Beispiel hierfür ist eine Addresse, welche aus Straße + Hausnummer, Postleitzahl und Ort besteht.  
Unterattribute werden mit ungerichteten Kanten mit dem zusammengesetzten Attribut verbunden.
Um ein zusammengetztes Attribut zu erstellen muss beim Erstellen des Attributs eine Liste von Unterattributen als Parameter ```composedOf``` übergeben werden.

#### Beispiel
_Eine Adresse besteht aus einer Straße + Hausnummer, einer PLZ und einem Ort._
``` python
g = ER()
g.add_node("Person")

g.add_attribute("Person", "Adresse", 
                composedOf=["Straße + Nr.", "PLZ", "Ort"])
g.display()                
``` 


---



### Mehrwertige Attribute

Ein (mehrwertiges) Attribut kann eine Menge von Werten enthalten. Ein Beispiel hierfür ist das Autor Attribut des Entity-Typ Buch, da ein Buch von mehreren Autoren geschrieben sein kann.  
Ein mehrwertiges Attribut wird als Ellipse mit doppelter Umrandung dargestellt.  
Um ein Attribut als mehrwertig zu kennzeichnen, muss der Parameter ```is_multiple``` auf wahr gesetzt werden.


#### Beispiel
_Ein Buch kann von mehreren Autoren geschrieben werden._  
_Natürlich nehmen wir in diesem Beispiel an, dass "Autor" keine Entität ist, sondern lediglich ein Attribut der Entität "Buch"._
``` python
g = ER()
g.add_node("Buch")

g.add_attribute("Buch", "Autoren", isMultiple=True)
g.display()
```

---


## Beziehungen zwischen Entity-Typen
> Neue Beziehung (=Relation) zwischen zwei Entitäten hinzufügen `add_relation()`

Oft stehen zwei oder mehr Entity-Typen in Beziehung zueinander. Beziehungen werden im ER-Diagramm durch Rauten dargestellt und können ebenfalls Attribute haben. 

Für die Kardinalitätsrestriktionen wurden in der Vorlesung zwei Notationen vorgestellt: die `1:n-Notation` und die `(min,max)-Notation`.  
Hierdurch können zusätzlich zur dargestellten Relation Kardinalitäten angegeben werden um darzustellen, in welcher Anzahl die Entitäten des einen Entity-Typen mit welcher Anzahl von Entitäten des anderen Entity-Typen in Beziehung stehen. 
Diese Kardinalitäten werden im ER-Diagramm an die Kanten zwischen Entity-Typ und Relation geschrieben. 

Der Befehl um eine Beziehung hinzuzufügen ist ```add_relation("From Entity-Type", "Relation name", "To Entity-Type", "n", "m")```.

``` python .noeval
g.add_relation(fromNodeLabel, relationLabel, 
               toNodeLabel, fromEdgeLabel, 
               toEdgeLabel, isWeak=False)
``` 

#### Funktionsparameter
- `fromNodeLabel(str)`: Bezeichnung des "from"-Knotens
- `relationLabel(str)`: Label der Relation
- `toNodeLabel(str)`: Label des "to"-Knotens
- `fromEdgeLabel(str)`: Label der "from"-Kante
- `toEdgeLabel(str)`: Beschriftung der "to"-Kante
- `isWeak(bool)`: Ist dies eine schwache Beziehung?

#### Beispiel
_Mehrere Patienten besuchen mehrere Ärzte. Zu jedem Besuch wird ein Datum gespeichert._
``` python
g = ER()
g.add_node("Arzt")
g.add_node("Patient")
g.add_relation("Patient", "besucht", "Arzt", "m", "n")
g.add_attribute("besucht", "Datum")
g.display()
```


---


### N-stellige Beziehungen

Es können auch drei oder mehr Entity-Typen in Beziehung zueinander stehen.  
Um weitere Entity-Typen einer Beziehung hinzuzufügen, kann der erste Parameter des ```add_relation``` Befehls leer ("") gelassen werden.

#### Beispiel
_Ein Professor prüft einen Studenten über eine Vorlesung._
``` python
g = ER()
g.add_node("Student")
g.add_node("Vorlesung")
g.add_node("Professor")
g.add_relation("Professor", "prüft", "Student", "prüft", "wird geprüft")
g.add_relation("", "prüft", "Vorlesung", "", "über")
g.display()
```


---


### Schwache Entity-Typen
Ein schwacher Entity-Typ ist von der Existenz des übergeordneten Entity-Typs abhängig.  

Schwache Entitätstypen werden im ER-Diagramm durch einen doppelten Rahmen um die Beziehung und eine doppelte Kante zwischen dem Beziehungsknoten, dem Entitätsknoten und der schwachen Entität gekennzeichnet. Außerdem werden die Schlüssel von schwachen Entity-Typen gestrichelt unterstrichen.  
Hierzu muss in allen drei Befehlen (```add_node```, ```add_relation```, ```add_attribute```) der Parameter ```isWeak``` auf ```True``` gesetzt werden.

#### Beispiel
_Ohne Hörsaalgebäude kann es keine Seminarräume geben._
``` python
g = ER()
g.add_node("Hörsaalgebäude")
g.add_node("Seminarraum", isWeak=True)
g.add_relation("Hörsaalgebäude", "liegt in", "Seminarraum", "(0,n)", "(1,1)", isWeak=True)
g.add_attribute("Seminarraum", "RaumNr", isPK=True, isWeak=True)
g.display()
```

---


## Generalisierung/Spezialisierung ("ist-ein" bzw. "is a")

Es kann Vererbungsbeziehungen (isA) zwischen Entity-Typen und spezialisierten Entity-Typen geben. Diese werden im ER-Diagramm als umgedrehte Dreiecke mit einer ungerichteten Kante zum allgemeinen Entity-Typen und einer oder mehreren gerichteten Kanten zu den spezialisierten Entity-Typen dargestellt. 

Es gibt unterschiedliche Formen dieser Vererbungsbeziehungen:
- **Disjunkt**
  - Spezialisierungen sind disjunkt (ein Angestellter kann nicht Assistent und Professor sein)
  - Pfeile zeigen in Richtung der Spezialisierung
- **Nicht disjunkt**
  - Spezialisierungen sind nicht disjunkt (Eine Person kann Angestellter und Student sein)
  - Pfeile Zeigen in Richtung der Generalisierung
- **Total (t)**
  - Die Dekomposition der Generalisierung ist vollständig (Es gibt entweder wissenschaftliche oder nicht wissenschaftliche Mitarbeiter)
  - Wird durch “t” neben der isA Beziehung dargestellt
- **Partiell (p)**
  - Die Vereinigung der Spezialisierung ist eine echte Untermenge der Generalisierung
  - Wird durch “p” neben der isA Beziehung dargestellt
 
Der Befehl um eine isA Beziehung zum ER-Diagramm hinzuzufügen ist ```add_is_a("Generalisation", ["Specialisation1","Specialisation2"], "p or t (partial or total)", isDisjunct=True/False)```

``` python .noeval
g.add_is_a(superClassLabel, subclassParam, 
           superLabel='', subLabel='', 
           isDisjunct=True)
```

#### Funktionsparameter
- `superClassLabel(str)`: Bezeichnung des Oberklassenknotens  (_"parent"/"superclass"_)
- `subclassParam(str oder Liste von str)`: Label des/der Unterklassenknoten(s) (_"child"/"subclass"_)
- `superLabel(str)`: Ist die Beziehung partiell oder total? ("p" oder "t" - geschrieben auf der Kante zur Oberklasse)
- `subLabel(str)`: Ist die Beziehung partiell oder total? ("p" oder "t" - wird auf die Kante zur Unterklasse geschrieben)
- `isDisjunct(bool)`: Sind die Elemente dieser Relation disjunkt?

#### Beispiel
``` python
g = ER()
g.add_node("Arzt")
g.add_node("Assistenzarzt")
g.add_node("Oberarzt")
g.add_node("Chefarzt")
g.add_is_a("Arzt", ["Assistenzarzt", "Oberarzt", "Chefarzt"], "p", isDisjunct=True)
g.display()
```

## ER und Relationales Datenmodell

### Entität mit Attributen
Der folgende Code erstellt die Relation
- Student(<u>MatrNr</u>, Name, Semester, Adresse)

``` python
g = ER()

g.add_node('Student') 

g.add_attribute('Student', 'MatrNr', isPK = True)
g.add_attribute('Student', 'Name')
g.add_attribute('Student', 'Semester', isMultiple = True)

g.add_attribute('Student', "Adresse", composedOf = ["Stadt", "Straße", "PLZ"])

g.display()
```

### Beziehungen zwischen Entitäten
Der folgende Code erstellt folgende...
#### Entitäten:
- Student(<u>MatrNr</u>)
- Vorlesung(<u>VorlNr</u>)
- Hört(<u>MatrNr</u>, <u>VorlNr</u>)


### Generalisierung / Spezialisierung (partielle Beziehung)

Der folgende Code erstellt folgende...

#### Entitäten:
- Angestellter(<u>PersNr</u>, Name)
- Professor(<u>PersNr</u>, Rang, Raum)
- Assistent(<u>PersNr</u>, Fachgebiet)

#### Interrelationale Abhängigkeiten:
- Professor[PersNr] $\subseteq$ Angestellter[PersNr]
- Assistent[PersNr] $\subseteq$ Angestellter[PersNr]

#### Partielle Beziehung:
- Professor[PersNr] $\cap$ Assistent[PersNr] = $\emptyset$

Professor und Assistent sind disjunkt *(ein Assistent kann **nicht** Professor sein).*  
Die Unterscheidung zwischen "total" und "partiell" wird *(manuell)* durch den Parameter `super_label` gesteuert.

``` python
g = ER()

g.add_node('Angestellter')
g.add_attribute('Angestellter', 'PersNr', isPK = True)
g.add_attribute('Angestellter', 'Name')

g.add_node('Professor')
g.add_node('Assistent')

g.add_is_a('Angestellter', ['Professor', 'Assistent'], superLabel = 'p', isDisjunct = True)

g.display()
```