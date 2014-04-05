## Login
POST /rest/user/login?{login}&{password}

## Get all projects
GET /rest/project/all{verbose} - if false, only shortnames and ids will returned

## Get list of issues
GET /rest/issue?{filter}&{with}&{max}&{after}