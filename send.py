import pyminizip
import tempfile
import stdio
import smtplib
from email.MIMEMultipart import MIMEMultipart
from email.MIMEText import MIMEText
from email.MIMEBase import MIMEBase
from email import encoders


def get_send_function(mail_from, smtp_server, smtp_port, mail_password_env_name):
    return lambda mail_to, filenames, subject, message, **args : \
        _send_files(mail_to, mail_from, filenames, subject, message,
            smtp_server=smtp_server, smtp_port=smtp_port, mail_password_env_name=mail_password_env_name, **args)


def _send_files(mail_to, mail_from, filenames, subject, message,
               directory4temp_archive = tempfile.mkdtemp(),
               archive_name = 'filesAttached.zip', password=None,
               max_size_for_mail = 4194304, smtp_server=None, smtp_port=None, mail_password_env_name=None):
    if isinstance(filenames, str):
        filenames = [filenames]
    temp_file_path = directory4temp_archive + '/' + archive_name
    get_zip_archive(filenames, temp_file_path, password)
    if os.path.getsize(temp_file_path) >  max_size_for_mail:
        send_file_via_wetransfer(temp_file_path, subject, message, mail_to, mail_from)
    else:
        send_file_via_mail(temp_file_path, subject, message, mail_to, mail_from, smtp_server, smtp_port, mail_password_env_name)
    os.remove(temp_file_path)


def get_zip_archive(filenames, output, passw=None, compression_lvl = 9):
    filens = list(filenames)
    for i, f in enumerate(filenames):
        if os.path.isdir(f):
            del filens[i]
            for fn in os.listdir(f):
                filens += [f + '/' + fn]
    stdio.verbose_func(pyminizip.compress_multiple, "Compressing : %s" % (",".join(filens)))\
        (filens, output, passw,compression_lvl)


def send_file_via_wetransfer(file, subject, message, mail_to, mail_from):
    __send_via_we_transfer( receiver=mail_to,
                            sender=mail_from,
                            message="SUBJECT:%s\n\nBODY:%s\n" %(subject, message),
                            fileslist=[file])

def send_file_via_mail(file, subject, message, mail_to, mail_from, smtp_server, smtp_port, mail_password_env_name):
    msg = MIMEMultipart()

    msg['From'] = mail_from
    msg['To'] = mail_to
    msg['Subject'] = subject

    body = message

    msg.attach(MIMEText(body, 'plain'))

    filename = file
    attachment = open(filename, "rb")

    part = MIMEBase('application', 'octet-stream')
    part.set_payload((attachment).read())
    encoders.encode_base64(part)
    part.add_header('Content-Disposition', "attachment; filename= %s" % filename)

    msg.attach(part)

    server = smtplib.SMTP(smtp_server, smtp_port)
    server.starttls()
    server.login(mail_from, os.getenv(mail_password_env_name))
    text = msg.as_string()
    server.sendmail(mail_from, mail_to, text)
    server.quit()


# Upload files or folders to WeTransfer
#
# VERSION       :1.0
# DATE          :2014-12-27
# AUTHOR        :Kevin Raynel <https://github.com/kraynel>
# URL           :https://github.com/kraynel/upload-wetransfer
# DEPENDS       :pip install requests requests-toolbelt


# usage :  upload-wetransfer.py [-h] [-r [RECEIVER [RECEIVER ...]]] [-s SENDER] [-m MESSAGE] [-R] files [files ...]

from urlparse import urlparse, parse_qs
from requests_toolbelt import MultipartEncoder, MultipartEncoderMonitor

import os, requests, sys, json, re, argparse, sys, mimetypes, collections

WE_TRANSFER_API_URL = "https://www.wetransfer.com/api/v1/transfers"
CHUNK_SIZE = 5242880

def getTransferId(sender, receivers, message):
    dataTransferId =  { "channel":"",
    "expire_in":   "",
    "from":    sender,
    "message": message,
    "pw" : "",
    "to[]" :   receivers,
    "ttype" :  "1",
    "utype" :  "js"
    }

    r = requests.post(WE_TRANSFER_API_URL, data=dataTransferId)
    response_data = json.loads(r.content)

    return response_data["transfer_id"]

def getFileObjectId(transferId, filename, filesize):
    dataFileObjectId =  { "chunked": "true",
    "direct":   "false",
    "filename":    filename,
    "filesize": filesize
    }

    r = requests.post((WE_TRANSFER_API_URL + "/{0}/file_objects").format(transferId), data=dataFileObjectId)
    response_data = json.loads(r.content)

    return response_data


def getChunkInfoForUpload(transferId, fileObjectId, chunkNumber, chunkSize=CHUNK_SIZE):
    dataChunk = { "chunkNumber" : chunkNumber,
    "chunkSize" :  chunkSize,
    "retries" : "0" }

    r = requests.put((WE_TRANSFER_API_URL + "/{0}/file_objects/{1}").format(transferId, fileObjectId), data=dataChunk)

    return json.loads(r.content)

def create_callback(previousChunks, fileSize):

    def callback(monitor, last_print_pct=[0]):
        pct = 100*float(previousChunks + monitor.bytes_read)/float(fileSize)
        if last_print_pct[0] + 5 < pct:
            last_print_pct[0]+= 5
            print("\t%2.f%%" % pct)

    return callback

def uploadChunk(chunkInfo, filename, dataBin, fileType, chunkNumber, fileSize):
    url = chunkInfo["url"]

    dataChunkUpload = collections.OrderedDict()
    for k, v in chunkInfo["fields"].items():
        dataChunkUpload[k] = v

    dataChunkUpload["file"] = (filename, dataBin, fileType)

    e = MultipartEncoder(fields=dataChunkUpload)
    m = MultipartEncoderMonitor(e, create_callback(chunkNumber*CHUNK_SIZE, fileSize))

    r = requests.post(url, data=m, headers={'Content-Type': e.content_type})
    print("")

def finalizeChunks(transferId, fileObjectId, partCount):
    dataFinalizeChunk = {
    "finalize_chunked"  : "true",
    "part_count"  : partCount
    }

    r = requests.put((WE_TRANSFER_API_URL + "/{0}/file_objects/{1}").format(transferId, fileObjectId), data=dataFinalizeChunk)
    #print(r.text)

def finalizeTransfer(transferId):
    print("Finalize transfer")

    r = requests.put((WE_TRANSFER_API_URL + "/{0}/finalize").format(transferId))

def cancelTransfer(transferId):
    print("Cancelling transfer")

    r = requests.put((WE_TRANSFER_API_URL + "/{0}/cancel").format(transferId))


def read_in_chunks(file_object, chunk_size=CHUNK_SIZE):
    """Lazy function (generator) to read a file piece by piece.
    Default chunk size: 5Mo."""
    while True:
        data = file_object.read(chunk_size)
        if not data:
            break
        yield data

def uploadFile(transferId, fileToUpload):
    with open(fileToUpload, 'rb') as f:
        fileMimeType = "application/octet-stream"
        #mimetypes.read_mime_types(f.name)
        fileSize = os.path.getsize(fileToUpload)
        fileName = os.path.basename(fileToUpload)

        dataFileObjectId = getFileObjectId(transferId, fileName, fileSize)
        if dataFileObjectId.has_key("url"):
            uploadChunk(dataFileObjectId, fileName, f.read(fileSize), fileMimeType, 0, fileSize)
            finalizeChunks(transferId, dataFileObjectId["file_object_id"], 1)
        else:
            chunkNumber = 1

            for piece in read_in_chunks(f):
                chunkInfo = getChunkInfoForUpload(transferId, dataFileObjectId["file_object_id"], chunkNumber, sys.getsizeof(piece))
                uploadChunk(chunkInfo, fileName, piece, fileMimeType, chunkNumber-1, fileSize)
                chunkNumber = chunkNumber + 1

            finalizeChunks(transferId, dataFileObjectId["file_object_id"], chunkNumber - 1)

def uploadDir(top, transferId, recursive):
    '''descend the directory tree rooted at top,
       calling the upload function for each regular file'''

    for root, dirs, files in os.walk(top):
        if not recursive:
            while len(dirs) > 0:
                dirs.pop()

        for name in files:
            print("Upload file : " + os.path.abspath(os.path.join(root, name)))
            uploadFile(transferId, os.path.abspath(os.path.join(root, name)))

def __send_via_we_transfer(fileslist = None, receiver=None, sender=None, message=None, recursive=False):
    # mimetypes.init()

    try:
        transferId = getTransferId(sender, receiver, message)

        for it in fileslist:
            if os.path.isfile(it):
                print("Upload file : " + it)
                uploadFile(transferId, it)
            elif os.path.isdir(it):
                uploadDir(it, transferId, recursive)
            else:
                print("Not a file/directory : " + it)


        finalizeTransfer(transferId)
    except KeyboardInterrupt:
        print ""
        if transferId:
            cancelTransfer(transferId)


if __name__ == '__main__':
    # send_files([ os.path.basename(__file__)], 'test', 'test succed')

    send_files([os.path.abspath('../../data/tables')], 'test', 'test succed')

    # send_files([os.path.abspath('../../data/tables/bla.txt')], 'test', 'test succed')