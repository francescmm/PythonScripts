from urllib.request import urlopen
from urllib.request import urlretrieve
import datetime
import sys

# Gets the content of a webpage or web resource
def getWebsource(url, encoding):
	response = urlopen(url)
	pageSource = ""
	
	if (len(encoding) > 0):
		pageSource = str(response.read(), encoding)
	else:
		pageSource = str(response.read())
		
	return pageSource

# Gets the substring between to patterns
def getSubstring(begin, end, text):
	startIndex = text.find(begin)
	endIndex = text.find(end)
	return (text[startIndex + len(begin):endIndex])

# Returns any of the strings we set are in today's BOPI. Otherwise it returns false.
# If today there isn't BOPI, it informs about that.
def isTextInTodaysBOPI(strings):
	currentDay = datetime.datetime.now().strftime("%A")
	
	if (currentDay.find("Sunday") == -1 and currentDay.find("Saturday") == -1):
		currentDay = datetime.datetime.now().strftime("%d-%m-%Y")

		url = "https://sede.oepm.gob.es/bopiweb/descargaPublicaciones/resultBusqueda.action?fecha=" + currentDay
		pageSource = getWebsource(url, 'utf-8')

		# We look for the MARCAS sectino
		textSlot = getSubstring("TOMO 1: MARCAS Y OTROS SIGNOS DISTINTIVOS", "TOMO 2: INVENCIONES", pageSource)
		
		# Checking that the file we're looking for is in XML format
		textSlot = getSubstring("en formato PDF", "en formato XML')", textSlot)

		# Finally, we get the UCM id to download the document
		textSlot = getSubstring("cargaForm('", "','xml')", textSlot)

		# Download the BOPI of the day and we check that the document contains the text we want to look for
		url = "https://sede.oepm.gob.es/bopiweb/DescargaDocumento?idUcm=" + textSlot + "&docTipo=xml"
		
		findText = getWebsource(url, '')
		
		found = False
		
		for f in strings:
			if findText.find(str(f)) != -1:
				found = True
				print (f, " found")
			else:
				print (f, " not found")
				
		if found:
			urlretrieve(url, "bopi_" + currentDay + ".xml")
	else:
		print ("Today there is no BOPI")

isTextInTodaysBOPI(sys.argv[1:])

