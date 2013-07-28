import argparse
import subprocess
import re

from nltk.tokenize import sent_tokenize


ap = argparse.ArgumentParser(description=__doc__,
                             formatter_class=argparse.RawTextHelpFormatter)
ap.add_argument('pdfs',
                metavar='PDF_FILES',
                nargs='+',
                help='database of geotokens')
ap.add_argument('--test',
                metavar='BINARY',
                type=lambda s: bool(int(s)),
                default=False,
                help='if 1, run doc tests')

args = ap.parse_args()


# PyPDF seems to output garbage more often than pdftotext, so we resort to
# system call.
#from PyPDF2 import PdfFileReader
#def pdf2txt_pypdf(pdf, limit):
#    text = ''
#    reader = PdfFileReader(open(pdf, 'rb'))
#    for (i, page) in enumerate(reader.pages):
#        text += page.extractText() + '\n'
#        if i > limit:
#            break
#    return text


def pdf2txt(pdf):
    #    process = subprocess.Popen(["pdftotext", pdf, '-'],
    process = subprocess.Popen(["pdftotext", '-layout', pdf, '-'],
                               shell=False,
                               stdout=subprocess.PIPE,
                               stderr=subprocess.STDOUT)
    content, err = process.communicate()[0:2]
    return content, err


def looks_like_finding_header(line):
    return re.match('.*(' +
                    'following recommendations' +
                    '|general findings' +
                    '|summary of findings' +
                    '|key findings' +
                    ').*', line.strip()[0:50].lower())


def clean_s(s):
    return re.sub(r'\s+', ' ', s).strip()


def filter_sentences(sentences):
    'Filter things that dont look like sentenes'
    return [clean_s(s) for s in sentences if len(s.strip()) > 30]


def summarize(lines, start, end):
    global num_keys
    text = ' '.join(lines[start:end])
    sentences = filter_sentences(sent_tokenize(text))
    num_keys += len(sentences)
    print '\n\t+++'.join(sentences)
    print '#sent=', len(sentences)


def extract_findings(pdf):
    global num_found
    text, err = pdf2txt(pdf)
    #print text
    lines = text.split('\n')
    found = False
    for (i, line) in enumerate(lines):
        if (looks_like_finding_header(line)):
            print 'HEADER:', clean_s(line)
            summarize(lines, i + 1, i + 20)
            found = True
    if found:
        num_found += 1


num_found = 0
num_keys = 0


def main():
    for pdf in args.pdfs:
        print '\n\nextracting from', pdf
        extract_findings(pdf)
    print 'found %d findings in %d/%d pdfs' % \
        (num_keys, num_found, len(args.pdfs))

if (__name__ == '__main__'):
    if args.test:
        import doctest
        doctest.testmod()
    else:
        main()
