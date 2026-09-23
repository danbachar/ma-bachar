ENTRY
  { address author booktitle chapter edition editor howpublished institution journal key month note number organization pages publisher school series title type volume year }
  {}
  { label }

INTEGERS { output.state before.all }

FUNCTION {output.bibitem}
{
  \bibitem{\citekey}
}

FUNCTION {format.lab.names}
{ 's :=
  #1 'nameptr :=
  s num.names$ 'numnames :=
  nameptr #1 >
    { s nameptr "{" format.name$ "}" * }
    { "" }
  if$
}

FUNCTION {format.lab.author}
{ author format.lab.names }

FUNCTION {format.lab.year}
{ year #2 #2 substring$ }

FUNCTION {make.label}
{
  format.lab.author " " * format.lab.year *
}

FUNCTION {article}
{ output.bibitem
  make.label
  "[" swap$ * "]" *
  " " *
  author "author" output.check
  title "title" output.check
  journal "journal" output.check
  year "year" output.check
  fin.entry
}

FUNCTION {book}
{ output.bibitem
  make.label
  "[" swap$ * "]" *
  " " *
  author "author" output.check
  title "title" output.check
  publisher "publisher" output.check
  year "year" output.check
  fin.entry
}

FUNCTION {inproceedings}
{ output.bibitem
  make.label
  "[" swap$ * "]" *
  " " *
  author "author" output.check
  title "title" output.check
  booktitle "booktitle" output.check
  year "year" output.check
  fin.entry
}

READ
EXECUTE {article}
EXECUTE {book}
EXECUTE {inproceedings}
