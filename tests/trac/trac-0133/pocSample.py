import pyxb
import poc

xml = open("poc.xml").read()
pobObject = poc.CreateFromDocument(xml, location_base="poc.xml")
print(pobObject.toxml("utf-8"))
