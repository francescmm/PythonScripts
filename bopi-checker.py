from urllib.request import urlopen
import datetime
import sys
import getopt
import re
import binascii
import threading
import base64
import os
import logging

class StoreImagesThread(threading.Thread):
    def __init__(self, id,  strings, date):
        self.id = id
        self.strings = strings
        self.date = date
        threading.Thread.__init__(self)

    def storeImagesFromXml(self, xmlStream):
       logging.info("{%d} Getting all the images from the BOPI" % self.id)
      
       startText = "<tns:imagen>data:image/jpg;base64,"
       endText = "</tns:imagen>"
       startIndex = xmlStream.find(startText)
       endIndex = xmlStream.find(endText)
       imgIndex = 0

       while (startIndex is not -1 or endIndex is not -1):
          imgSrc = xmlStream[startIndex + len(startText):endIndex]
          xmlStream = xmlStream[startIndex + len(startText) + len(imgSrc) + len(endText):]
      
          try:
              imgdata = base64.b64decode(imgSrc)
              filename = "images\\" + self.date + "\\img_" + str(imgIndex) + ".jpg"

              os.makedirs(os.path.dirname(filename), exist_ok = True)
              with open(filename, 'wb') as f:
                 f.write(imgdata)
         
              imgIndex += 1
              startIndex = xmlStream.find(startText)
              endIndex = xmlStream.find(endText)
          except binascii.Error:
              logging.info("{%d} Image format invalid." & self.id)

    def getTodaysBOPI(self):
       logging.info("{%d} Accessing to the OEPM to get the BOPI of %s..." % (self.id, self.date))
   
       day = 0
   
       if (len(self.date) != 0):
          repeat = True
          day = datetime.datetime.strptime(self.date, '%d-%m-%Y').weekday()
       else:
          day = datetime.datetime.now().weekday()
         
       if day >= 0 and day < 5:
          if len(self.date) == 0:
             self.date = datetime.datetime.now().strftime('%d-%m-%Y')
        
          url = "https://sede.oepm.gob.es/bopiweb/descargaPublicaciones/resultBusqueda.action?fecha=" + self.date
          pageSource = getWebsource(url, 'utf-8')

          # We look for the MARCAS section
          logging.info("{%d} Looking for the document ID" % self.id)
          textSlot = getSubstring("TOMO 1", "TOMO 2", pageSource)

          if textSlot.find("error") != -1:
              logging.info("{%d} There is no BOPI." % self.id)
              return
      
          # Checking that the file we're looking for is in XML format
          textSlot = getSubstring("en formato PDF", "en formato XML')", textSlot)

          # Finally, we get the UCM id to download the document
          logging.info("{%d} Getting the UCM id" % self.id)
          textSlot = getSubstring("cargaForm('", "','xml')", textSlot)

          # Download the BOPI of the day and we check that the document
          # contains the text we want to look for
          url = "https://sede.oepm.gob.es/bopiweb/DescargaDocumento?idUcm=" + textSlot + "&docTipo=xml"

          logging.info("{%d} Getting the XML file from the server" % self.id)
      
          findText = getWebsource(url, '')
      
          found = printFoundStrings(findText, self.strings)
          
          if found:
             logging.info("{%d} Results found on %s" % (self.id, self.date))
      
          logging.info("{%d} Saving the XML file in local filesystem" % self.id)
      
          filename = "bopi\\bopi_" + self.date + ".xml"
          os.makedirs(os.path.dirname(filename), exist_ok = True)
      
          with open(filename, 'w') as f:
             f.write(findText)
         
          self.storeImagesFromXml(findText)

       else:
          logging.info("{%d} There is no BOPI." % self.id)

    def run(self):
        logging.info("{%d} Starting thread for day %s" % (self.id, self.date))
        self.getTodaysBOPI()
        logging.info("{%d} Ending thread" % self.id)

# Gets the content of a webpage or web resource
def getWebsource(url, encoding):
   try:
       response = urlopen(url)
       pageSource = ""
   
       if (len(encoding) > 0):
          pageSource = str(response.read(), encoding)
       else:
          pageSource = str(response.read())

       return pageSource
   except UnicodeEncodeError:
       logging.error("Error while reading web page: %s" % url)
       return ""

# Gets the substring between to patterns
def getSubstring(begin, end, text):
   startIndex = text.find(begin)
   endIndex = text.find(end)
   return (text[startIndex + len(begin):endIndex])

def printFoundStrings(text, strings):
    for f in strings:
        if text.find(str(f).upper()) != -1 or text.find(str(f).lower()) != -1:
            return True

    return False

def main(argv):
   startDate = ''
   words = []
   allFrom = False
   logging.basicConfig(format='%(asctime)s %(message)s', filename='bopi-checker.log', level=logging.INFO)
   logging.info(">> Started execution")
   try:
      opts, args = getopt.getopt(argv,"hd:rw:",["date=","words=","recursive"])
   except getopt.GetoptError:
      print('bopi-checker.py -d <startDate format dd-MM-yyyy> -w <words separated by comma>')
      sys.exit(2)
      
   for opt, arg in opts:
      if opt == '-h':
         print('bopi-checker.py -d <startDate format dd-MM-yyyy> -w <words separated by comma>')
         sys.exit()
      elif opt in ("-d", "--date"):
         match = re.search(r'(\b\d{1,2}[-/:]\d{1,2}[-/:]\d{4}\b)', arg)
         if match is not None and (datetime.datetime.strptime(arg, '%d-%m-%Y') <= datetime.datetime.now()):
            startDate = arg
         else:
            print('The date must be valid and equal or lower than today.')
            sys.exit()
      elif opt in ("-w", "--words"):
         words = arg.split(",")
      elif opt in ("-r", "--recursive"):
         allFrom = True
   
   severalDays = len(startDate) != 0
   userDate = datetime.datetime.now()

   if severalDays:
       userDate = datetime.datetime.strptime(startDate, '%d-%m-%Y')

   count = 1
   threadList = []
   while userDate <= datetime.datetime.now():
      startDate = datetime.datetime.strftime(userDate, '%d-%m-%Y')

      imgThread = StoreImagesThread(count, words, startDate)
      imgThread.start()
      threadList.append(imgThread);

      if not allFrom:
         userDate = datetime.datetime.now()

      userDate += datetime.timedelta(days = 1)
      count += 1

   for thread in threadList:
      thread.join()

   logging.info(">> Ended execution")

if __name__ == "__main__":
   main(sys.argv[1:])

