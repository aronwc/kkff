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


def filter_sentences(sentences):
    'Filter things that dont look like sentenes'
    pass


def summarize(lines, start, end):
    text = ' '.join(lines[start:end])
    sentences = sent_tokenize(text)
    print sentences
    print '#sent=', len(sentences)


def extract_findings(pdf):
    text, err = pdf2txt(pdf)
    #print text
    lines = text.split('\n')
    for (i, line) in enumerate(lines):
        if (looks_like_finding_header(line)):
            print 'HEADER:', line
            summarize(lines, i + 1, i + 20)


def main():
    for pdf in args.pdfs:
        print '\n\nextracting from', pdf
        extract_findings(pdf)

if (__name__ == '__main__'):
    if args.test:
        import doctest
        doctest.testmod()
    else:
        main()
