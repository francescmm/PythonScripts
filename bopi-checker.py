from urllib.request import urlopen
from urllib.request import urlretrieve
import datetime

# Gets the content of a webpage or web resource
def getWebsource(url):
	response = urlopen(url)
	pageSource = str(response.read())
	return pageSource

# Gets the substring between to patterns
def getSubstring(begin, end, text):
	startIndex = text.find(begin)
	endIndex = text.find(end)
	return (text[startIndex + len(begin):endIndex])

# Gets the index of the text we're looking for. If the text isn't found  prints -1.
# If today there isn't BOPI, it informs about that
def isTextInTodaysBOPI(text):
	currentDay = datetime.datetime.now().strftime("%A")

	if (currentDay.find("Sunday") != -1 and currentDay.find("Saturday") != -1):
		currenDay = datetime.datetime.now().strftime("%d-%m-%Y")

		url = "https://sede.oepm.gob.es/bopiweb/descargaPublicaciones/resultBusqueda.action?fecha=" + currenDay
		pageSource = getWebsource(url)

		# We look for the MARCAS sectino
		textSlot = getSubstring("TOMO 1: MARCAS Y OTROS SIGNOS DISTINTIVOS", "TOMO 2: INVENCIONES", pageSource)

		# Checking that the file we're looking for is in XML format
		textSlot = getSubstring("en formato PDF", "en formato XML')", textSlot)

		# Finally, we get the UCM id to download the document
		textSlot = getSubstring("cargaForm('", "','xml')", textSlot)

		# Download the BOPI of the day and we check that the document contains the text we want to look for
		url = "https://sede.oepm.gob.es/bopiweb/DescargaDocumento?idUcm=" + textSlot + "&docTipo=xml"
		findText = getWebsource(url)

		return findText.find(text)
	else:
		return "Today there is no BOPI"

print (isTextInTodaysBOPI("my text"))

