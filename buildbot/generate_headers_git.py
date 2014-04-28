# vim: set ts=8 sts=2 sw=2 tw=99 et:
import re
import os, sys
import subprocess

argv = sys.argv[1:]
if len(argv) < 2:
  sys.stderr.write('Usage: generate_headers.py <source_path> <output_folder>\n')
  sys.exit(1)

SourceFolder = os.path.abspath(os.path.normpath(argv[0]))
OutputFolder = os.path.normpath(argv[1])

def get_git_version():
  argv = ['git', '--work-tree', SourceFolder, 'rev-parse', 'HEAD']
  
  # Python 2.6 doesn't have check_output.
  if hasattr(subprocess, 'check_output'):
    text = subprocess.check_output(argv)
    if str != bytes:
      text = str(text, 'utf-8')
  else:
    p = subprocess.Popen(argv, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    output, ignored = p.communicate()
    rval = p.poll()
    if rval:
      raise subprocess.CalledProcessError(rval, argv)
    text = output.decode('utf8')

  return text.rstrip('\n')

def output_version_headers():
  cset = get_git_version()
  rev = cset

  with open(os.path.join(SourceFolder, 'product.version')) as fp:
    contents = fp.read()
  m = re.match('(\d+)\.(\d+)\.(\d+)-?(.*)', contents)
  if m == None:
    raise Exception('Could not detremine product version')
  major, minor, release, tag = m.groups()
  fullstring = "{0}.{1}.{2}".format(major, minor, release)
  if tag != "":
    fullstring += "-{0}".format(tag)
    if tag == "dev":
      fullstring += "+{0}".format(rev)

  with open(os.path.join(OutputFolder, 'version_auto.h'), 'w') as fp:
    fp.write("""
#ifndef _AUTO_VERSION_INFORMATION_H_
#define _AUTO_VERSION_INFORMATION_H_

#define BUILD_TAG		\"{0}\"
#define BUILD_REV		\"{1}\"
#define BUILD_CSET		\"{2}\"
#define BUILD_MAJOR		\"{3}\"
#define BUILD_MINOR		\"{4}\"
#define BUILD_RELEASE	\"{5}\"

#define BUILD_UNIQUEID BUILD_REV \":\" BUILD_CSET

#define VERSION_STRING	\"{6}\"
#define VERSION_FILE		{7},{8},{9},0

#endif /* _AUTO_VERSION_INFORMATION_H_ */
    """.format(tag, rev, cset, major, minor, release, fullstring, major, minor, release))

output_version_headers()
