# v0.11.1 (17/07/17)

- Add logging kwarg to FlumpBlueprint

# v0.11.0 (29/06/17)

- The name of the view as passed to flask can now be customized via
  `VIEW_NAME`.  This also allows us a single blueprint to contiain multiple
  flump views with the same RESOURCE_NAME.

# v0.10.1 (24/05/17)

- Set mimetype only if empty to support different content types.

# v0.10.0 (04/05/17)

- Add initial URL_MAPPING feature to support custom URL schemes for views.

# v0.9.1 (17/01/17)

- Make HTTP method classes inherit from `object`, for better integration with python 2

# v0.9.0 (13/01/17)

- Refactor FlumpView construction (This is a massively breaking change.)

# v0.8.0 (16/08/16)

- Flump now supports running on python 2
- EntityData is now created in it's own function, making it easier to use flump
  with models that don't expose `.id` & `.etag` properties.
- The test directory is no longer included in the packages in setup.py

# v0.7.8 (06/07/16)

- Pagination links now keep any non-pagination query string parmaeters that
  are in the current request.

# v0.7.7 (04/07/16)

- Stopped redirecting to "canonical" URLs if an expected trailing slash was
  missing.  URLs should now be matched regardless of whether they have a
  trailing slash or not.

# v0.7.6 (11/05/16)

- Include etags as part of entity `meta` section.
- Add current page and size to response `meta` section for paginated responses.

# v0.7.5 (11/05/16)

- Handle endpoints without trailing slashes better.
- Add a default BadRequest handler.

# v0.7.4 (06/05/16)

- Fix issue with previous release change being reverted

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
