# Julee Knowledge Service

This is a reference implementation of a julee architecture component.
Or it will be - it's a jumble of files at the moment.

The knowledge service stores things in collections,
and then supports queries (of things or of collections).
Sounds simple, but the Knowledge Services process and interprets
the things it stores, so what's queried is not the thing(s) itself,
but the processed interpretation of the thing(s).

They can be specialists, with two types of expertise:
- formats and structure, e.g. processing specific file types
- knowledge domains, e.g. bringing intrinsic expertise to the interpretation

This reference implementation aims to support a useful collection of formats,
and be an extension point for those
who wish to process their own perculiar flavours of data.

The reference implentation also aims to serve as an example
of how implementers might leverage proprietary knowledge
during information processed,
and surface it as expertise at query time.
