# v0.7.4 (06/05/16)

- Fix issue with previosu release change being reverted

# v0.7.3 (06/05/16)

- Don't try and parse JSON in default logger.

# v0.7.2 (06/05/16)

- Ensure `application/vnd.api+json` mimetype works for POST/PATCH requests. Also allow `application/json` mimetype, and no specified mimetype.

# v0.7.1 (01/04/16)

- Increase default max_page_size to 100, because 20 is unreasonably small.

# v0.7.0 (08/03/16)

Note: This is a breaking change, but as we haven't released yet we aren't
bumping the major version.

- Heavily refactor the API.  See README & documentation for the new API.
- Trying to print an Immutable validator will no longer except (#14).

# v0.6.0 (15/02/16)

Note: This is a breaking change, but as we haven't released yet we aren't bumping the major version.

- Remove FlumpSchema and instead direct users to use a `marshmallow.Schema`
- Provide `update_entity` and `create_entity` stubs on the `Patch` and `Post` mixins respectively.

# v0.5.0 (19/11/15)

- Fix immutable validator to not return the value as this would cause an issue if the value was `False`.
- Add Sphinx documentation

# v0.4.1 (17/11/15)

- Add Immutable validator

# v0.4.0 (10/11/15)

- Add GET MANY support
- Add basic pagination mixin

# v0.3.0 (04/11/15)

- Add PATCH support for updating entities
- Better Etag handling

# v0.2.0 (03/11/15)

- Allow endpoints to take arbitrary kwargs
- Rearrange HTTP methods to mixin classes so clients can decide which to expose

# v0.1.2 (30/10/15)

Minor fix to logging.

# v0.1.1 (30/10/15)

Minor fix to setup.py

# v0.1.0 (30/10/15)

Initial Release
