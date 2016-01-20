.. :changelog:

History
=======

0.2.2 (2016-01-20)
------------------
- Support for liftover of BAMs (includes a workaround for Crossmap bug that
  segfaulted on liftovers with a specified output filename in the test
  environment).
- When lifting over between assemblies and the source assembly doesn't match
  what is configured for a track, raise a ValueError.
- For lifted-over studies, the `metadata.yaml` config keeps track of the
  liftover history in the new `study/liftover` section
- improved test environment setup
- improved tests (checking for existence of uploaded files)


0.2.1 (2015-12-05)
------------------
- if the `description` field is empty or missing, fill in the contents of
  README as documentation.
- add functools32 to requirements.txt (thanks Titus Brown)
- fixes to `hubward liftover`:
    - downloaded chainfiles are cached
    - skip tracks where assembly of track differs from the requested
      `--from_assembly`
    - upon lifting over, add a note to the description of the study's
      metadata.yaml to reflect this and also as a comment in the YAML file.
    - workaround for a bug in CrossMap on BED9+ files. The thickStart and
      thickEnd fields were not being lifted over correctly.
- use pycurl for downloading for better handling of URL redirects. This
  happens, for example, when downloading supplemental data from ScienceDirect
- less verbose bigbed/bigwig conversion
- allow optional fields in metadata to be blank
- improvements to testing framework


0.2.0 (2015-10-24)
------------------
Streamlining of the code and CLI. This causes some backward
incompatibility with `metadata.yaml` config files in version 0.1.0, in
particular, the "source" section is now required. There is now a defined schema
for the metadata and the grouping files so that future changes can be validated
and automatically fixed.


0.1.0 (2014-01-11)
---------------------

* First release on PyPI.
