# See https://docs.djangoproject.com/en/dev/howto/deployment/checklist/

# {{{ database and site

USING_LOCAL_TEST_SETTINGS = True
# test script
# python manage.py test --local_test_settings test_local_settings.py
# coverage run manage.py test tests --local_test_settings test_local_settings.py
# python manage.py test tests.test_my_local --local_test_settings test_local_settings.py



import os, platform
BASE_DIR = os.path.dirname(__file__)

SECRET_KEY = '<CHANGE ME TO SOME RANDOM STRING ONCE IN PRODUCTION>'

ALLOWED_HOSTS = [
        "*",
        ]

# Configure the following as url as above.
RELATE_BASE_URL = "http://YOUR/RELATE/SITE/DOMAIN"

# {{{ my specific
SENDFILE_URL = '/protected'
SENDFILE_BACKEND = 'sendfile.backends.development'

# This MUST be different from the value in local_settings.py
# To prevent your production data from being delete,
# the folder must be named "test_protected"
SENDFILE_ROOT = os.path.join(BASE_DIR, 'test_protected')

MEDIA_URL = '/media/'

MEDIA_ROOT = os.path.join(BASE_DIR, "test_media")

RELATE_MONGODB_NAME = "test_learningwhat_mongodb"

# don't configure this for production!
RELATE_MONGO_CLIENT_PATH = "mongomock.MongoClient"

RELATE_LATEX_SETTINGS = {
    "latex": {
        "RELATE_LATEX_DATAURI_MONGO_COLLECTION_NAME":
            "test_learningwhat_latex_datauri",
        "RELATE_LATEX_ERROR_MONGO_COLLECTION_NAME":
            "test_learningwhat_latex_error"
    },
    "bin_path": {},
    "latex_page": {
        "RELATE_LATEX_PAGE_COLLECTION_NAME":
            "test_learningwhat_latex_page",
        "RELATE_LATEX_PAGE_PART_COLLECTION_NAME":
            "test_learningwhat_latex_page_part",
        "RELATE_LATEX_PAGE_COMMITSHA_TEMPLATE_PAIR_COLLECTION":
            "test_learningwhat_latex_page_commitsha_template_pair",
    }
}

if platform.system().lower().startswith("win"):
    # requires ImageMagick >=7.0.1
    if platform.node() == "Dzhuang-surface":
        imagemagick_path = r"C:\Program Files\ImageMagick-7.0.7-Q16"
    else:
        imagemagick_path = r"D:\Program Files\ImageMagick-7.0.7-Q8"
    RELATE_LATEX_SETTINGS["bin_path"].update(
        {"RELATE_IMAGEMAGICK_BIN_DIR": imagemagick_path})

RELATE_CUSTOM_BOWER_INSTALLED_APPS = (
    "pdf.js=https://github.com/mozilla/pdf.js/releases/download/v1.3.91/pdfjs-1.3.91-dist.zip",
    "jquery-file-upload",
    "blueimp-gallery",

    ## IE9 below support of HTML5 elements and media queries
    "html5shiv",
    "respond",

    #"jquery-form",
    "cropper",

    # https://clipboardjs.com/
    "clipboard",
    "marked",
    "ez-plus",

    # for survey
    'jquery-form',
    'jcarousel',
    'bootstrap-datepicker',

    # for sortable table rows in image_upload
    'jqueryui-touch-punch',
    )

RELATE_CUSTOM_INSTALLED_APPS = (
    'django.contrib.sites',
    'image_upload',
    'imagekit',
    "djcelery_email",
    "survey",
    "questionnaire",
    )

SITE_ID = 1

from relate import customized
RELATE_USER_FULL_NAME_FORMAT_METHOD = customized.format_full_name

RELATE_LATEX_TO_IMAGE_ENABLED = True

RELATE_LATEX_SETTINGS = {
    "latex": {

    },
    "bin_path": {

    },
    "latex_page": {

    }
}

JINJA2_MACRO = {
    "latex": "plugins.latex.jinja_tex_to_img_tag"
}

CHECK = [
    "plugins.latex.check.latex2image_bin_check"
]

RELATE_CUSTOM_PAGE_CLASSES = [
    ("ImageUploadQuestion",
        "image_upload.page.imgupload.ImageUploadQuestion"),
    ("LatexRandomImageUploadQuestion",
        "image_upload.page.latexpage.LatexRandomImageUploadQuestion"),
    ("LatexRandomCodeQuestion",
        "image_upload.page.latexpage.LatexRandomCodeQuestion"),
    ("LatexRandomCodeQuestionWithHumanTextFeedback",
        "image_upload.page.latexpage.LatexRandomCodeQuestionWithHumanTextFeedback"),
    ("LatexRandomChoiceQuestion",
        "image_upload.page.latexpage.LatexRandomChoiceQuestion"),
    ("LatexRandomMultipleChoiceQuestion",
        "image_upload.page.latexpage.LatexRandomMultipleChoiceQuestion"),
    ("LatexRandomCodeTextQuestion",
        "image_upload.page.latexpage.LatexRandomCodeTextQuestion"),
    ("LatexRandomCodeInlineMultiQuestion",
        "image_upload.page.latexpage.LatexRandomCodeInlineMultiQuestion"),
    ("PythonCodeQuestionWithPageContext",
        "course.page.code_with_page_context.PythonCodeQuestionWithPageContext"),
]

import platform

if platform.system().lower().startswith("win"):
    RELATE_LATEX_SETTINGS["bin_path"].update(
        {"RELATE_IMAGEMAGICK_BIN_DIR":
            r"D:\Program Files\ImageMagick-7.0.7-Q8"})
else:
    RELATE_LATEX_SETTINGS["bin_path"].update(
        {"RELATE_LATEX_BIN_DIR":
            "/usr/local/texlive/2015/bin/x86_64-linux"})
#}}}


# Uncomment this to use a real database. If left commented out, a local SQLite3
# database will be used, which is not recommended for production use.
#
# DATABASES = {
#     'default': {
#         'ENGINE': 'django.db.backends.postgresql_psycopg2',
#         'NAME': 'relate',
#         'USER': 'relate',
#         'PASSWORD': '<PASSWORD>',
#         'HOST': '127.0.0.1',
#         'PORT': '5432',
#     }
# }

# Recommended, because dulwich is kind of slow in retrieving stuff.
#
# Also, progress bars for long-running operations will only work
# properly if you enable this. (or a similar out-of-process cache
# backend)
#
# You must 'pip install pylibmc' to use this (which in turn may require
# installing 'libmemcached-dev').
#
# Btw, do not be tempted to use 'MemcachedCache'--it's unmaintained and
# broken in Python 33, as of 2016-08-01.
#
# CACHES = {
#     'default': {
#         'BACKEND': 'django.core.cache.backends.memcached.PyLibMCCache',
#         'LOCATION': '127.0.0.1:11211',
#     }
# }

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

TIME_ZONE = "America/Chicago"

# }}}

# {{{ git storage

# Your course git repositories will be stored under this directory.
# Make sure it's writable by your web user.
#
# The default below makes them sit side-by-side with your relate checkout,
# which makes sense for development, but you probably want to change this
# in production.
#
# The 'course identifiers' you enter will be directory names below this root.

#GIT_ROOT = "/some/where"
GIT_ROOT = ".."

# }}}

# {{{ email

EMAIL_HOST = '127.0.0.1'
EMAIL_HOST_USER = ''
EMAIL_HOST_PASSWORD = ''
EMAIL_PORT = 25
EMAIL_USE_TLS = False

ROBOT_EMAIL_FROM = "Example Admin <admin@example.com>"
RELATE_ADMIN_EMAIL_LOCALE = "en_US"

SERVER_EMAIL = ROBOT_EMAIL_FROM

ADMINS = (
    ("Example Admin", "admin@example.com"),
    )

# If your email service do not allow nonauthorized sender, uncomment the following
# statement and change the configurations above accordingly, noticing that all
# emails will be sent using the EMAIL_ settings above.
#RELATE_EMAIL_SMTP_ALLOW_NONAUTHORIZED_SENDER = False

# Advanced email settings if you want to configure multiple SMTPs for different
# purpose/type of emails. It is also very useful when
# "RELATE_EMAIL_SMTP_ALLOW_NONAUTHORIZED_SENDER" is False.
# If you want to enable this functionality, set the next line to True, and edit
# the next block with your cofigurations.
RELATE_ENABLE_MULTIPLE_SMTP = False

if RELATE_ENABLE_MULTIPLE_SMTP:
    EMAIL_CONNECTIONS = {

        # For automatic email sent by site.
        "robot": {
            # You can use your preferred email backend.
            'backend': 'djcelery_email.backends.CeleryEmailBackend',
            'host': 'smtp.gmail.com',
            'username': 'blah@blah.com',
            'password': 'password',
            'port': 587,
            'use_tls': True,
        },

        # For emails that expect no reply for recipients, e.g., registration,
        # reset password, etc.
        "no_reply": {
            'host': 'smtp.gmail.com',
            'username': 'blah@blah.com',
            'password': 'password',
            'port': 587,
            'use_tls': True,
        },

        # For sending notifications like submission of flow sessions.
        "notification": {
            'host': 'smtp.gmail.com',
            'username': 'blah@blah.com',
            'password': 'password',
            'port': 587,
            'use_tls': True,
        },

        # For sending feedback email to students in grading interface.
        "grader_feedback": {
            'host': 'smtp.gmail.com',
            'username': 'blah@blah.com',
            'password': 'password',
            'port': 587,
            'use_tls': True,
        },

        # For student to send email to course staff in flow pages
        "student_interact": {
            'host': 'smtp.gmail.com',
            'username': 'blah@blah.com',
            'password': 'password',
            'port': 587,
            'use_tls': True,
        },

        # For enrollment request email sent to course instructors
        "enroll": {
            'host': 'smtp.gmail.com',
            'username': 'blah@blah.com',
            'password': 'password',
            'port': 587,
            'use_tls': True,
        },
    }

    # This will be used as default connection when other keys are not set.
    EMAIL_CONNECTION_DEFAULT = "robot"

    NO_REPLY_EMAIL_FROM = "Noreply <noreply_example@example.com>"
    NOTIFICATION_EMAIL_FROM = "Notification <notification_example@example.com>"
    GRADER_FEEDBACK_EMAIL_FROM = "Feedback <feedback_example@example.com>"
    STUDENT_INTERACT_EMAIL_FROM = "interaction <feedback_example@example.com>"
    ENROLLMENT_EMAIL_FROM = "Enrollment <enroll@example.com>"


# }}}


# Cool down time (seconds) required before another new session of a flow
# is allowed to be started.
RELATE_SESSION_RESTART_COOLDOWN_SECONDS = 10


# {{{ sign-in methods

RELATE_SIGN_IN_BY_EMAIL_ENABLED = True
RELATE_SIGN_IN_BY_USERNAME_ENABLED = True
RELATE_REGISTRATION_ENABLED = False
RELATE_SIGN_IN_BY_EXAM_TICKETS_ENABLED = True

# If you enable this, you must also have saml_config.py in this directory.
# See saml_config.py.example for help.
RELATE_SIGN_IN_BY_SAML2_ENABLED = False

# }}}

# {{{ editable institutional id before verification?

# If set to False, user won't be able to edit institutional ID
# after submission. Set to False only when you trust your students
# or you don't want to verfiy insitutional ID they submit.
RELATE_EDITABLE_INST_ID_BEFORE_VERIFICATION = True

# If set to False, these fields will be hidden in the user profile form.
RELATE_SHOW_INST_ID_FORM = True
RELATE_SHOW_EDITOR_FORM = True

# }}}

# Whether disable "markdown.extensions.codehilite" when rendering page markdown.
# Default to True, as enable it sometimes crashes for some pages with code fences.
# For this reason, there will be a warning when the attribute is set to False when
# starting the server.
#RELATE_DISABLE_CODEHILITE_MARKDOWN_EXTENSION = True

# {{{ user full_name format

# RELATE's default full_name format is "'%s %s' % (first_name, last_name)",
# you can override it by supply a customized method/fuction, with
# "firstname" and "lastname" as its paramaters, and return a string.

# For example, you can define it like this:

#<code>
#   def my_fullname_format(firstname, lastname)
#         return "%s%s" % (last_name, first_name)
#</code>

# and then uncomment the following line and enable it with:

#RELATE_USER_FULL_NAME_FORMAT_METHOD = my_fullname_format

# You can also import it from your custom module.

# }}}

# {{{ system email appelation priority

# RELATE's default email appelation of the receiver is a ordered list:
# ["first_name", "email", "username"], when first_name is not None
# (e.g, first_name = "Foo"), the email will be opened
# by "Dear Foo,". If first_name is None, then email will be used
# as appelation, so on and so forth.

# you can override the appelation priority by supply a customized list
# named RELATE_EMAIL_APPELATION_PRIORITY_LIST. The available
# elements include first_name, last_name, get_full_name, email and
# username.

# RELATE_EMAIL_APPELATION_PRIORITY_LIST = [
#         "full_name", "first_name", "email", "username"]

# }}}

# {{{ extra checks

# This allow user to add customized startup checkes for user-defined modules
# using Django's system checks (https://docs.djangoproject.com/en/dev/ref/checks/)
# For example, define a `my_check_func in `my_module` with
# <code>
#   def my_check_func(app_configs, **kwargs):
#         return [list of error]
#</code>
# The configuration should be
# RELATE_STARTUP_CHECKS_EXTRA = ["my_module.my_check_func"]
# i.e., Each item should be the path to an importable check function.
#RELATE_STARTUP_CHECKS_EXTRA = []

# }}}

# {{{ convert LaTeX to image settings

# To enable tex2img functionality, uncomment the following line.
#RELATE_LATEX_TO_IMAGE_ENABLED = True

# The bin dir of tex compiler and image converter should be
# correctly configured or RELATE will failed to start.
#RELATE_LATEX_BIN_PATH = "/usr/local/texlive/2015/bin/x86_64-linux"
#RELATE_IMAGEMAGICK_BIN_DIR = "/path/to/imagemagic/convert/bin/"

# configure the following only if dvisvgm or dvipng can't be found
# in sys evn..
#RELATE_DVISVGM_BIN_DIR = "/path/to/dvisvgm/bin/"
#RELATE_DVIPNG_BIN_DIR = "/path/to/dvipng/bin/"

# image, especially svg have large file size, files with size
# exceed the following won't be cached.
RELATE_IMAGE_CACHE_MAX_BYTES = 65536

# }}}

# {{{ docker

# A string containing the image ID of the docker image to be used to run
# student Python code. Docker should download the image on first run.
RELATE_DOCKER_RUNPY_IMAGE = "dzhuang/learning-what-runpy-i386"
#RELATE_DOCKER_RUNPY_IMAGE = "inducer/relate-runpy-i386"
# A URL pointing to the Docker command interface which RELATE should use
# to spawn containers for student code.

# This should be used for local docker on linux
RELATE_DOCKER_URL = "unix://var/run/docker.sock"
#RELATE_DOCKER_URL = "http://183.6.143.4:2375"

RELATE_DOCKER_TLS_CONFIG = None

# Use another ECS instance to host runpy
USE_ANOTHER_ECS_FOR_RUNPY_DOCKER = True

if USE_ANOTHER_ECS_FOR_RUNPY_DOCKER:
    import docker.tls

    if "Windows" in platform.system():
        ca_folder = r"D:\document\client"
    else:
        ca_folder = "/home/course/client-tls"

    RELATE_DOCKER_TLS_CONFIG = docker.tls.TLSConfig(
        client_cert=(
            os.path.join(ca_folder, "cert.pem"),
            os.path.join(ca_folder, "key.pem"),
            ),
        ca_cert=os.path.join(ca_folder, "ca.pem"),
        verify=True)


RELATE_RUNPY_DOCKER_ENABLED = True

# Docker configurations used by Relate. For runpy Docker (code pages), which requires
# the "docker_image" (with previous value "RELATE_DOCKER_RUNPY_IMAGE") key, the
# config name is default to "default". You can switch the name to other by
# configuring "RELATE_RUNPY_DOCKER_CLIENT_CONFIG_NAME".
RELATE_DOCKERS = {
    "default": {
        "docker_image": RELATE_DOCKER_RUNPY_IMAGE,
        "client_config": {
            "base_url": RELATE_DOCKER_URL,
            "tls": RELATE_DOCKER_TLS_CONFIG,
            "timeout": 15,
            "version": "1.19"
        },
        "local_docker_machine_config": {
            "enabled": True,
            "config":{
                "shell": None,
                "name": "default",
            },
        },

        # This is required to be configured for relate runpy docker for running code
        # quetsions (and other cases when you need to used the
        # get_connect_ip_and_port_by_container_from_config method),
        # in cases when your RELATE instance and (runpy) docker-running
        # instances are not on the same subnet. You must know the private ip and
        # a correspond public ip (by which the RElATE instance can visit the docker
        # instance) of each docker-running instances.
        # Dict format: {private_ip1: public_ip_1, private_ip2, public_ip_2}
        "private_public_ip_map_dict": {},
        "execution_host_alias_dict": {},
    },
    "other":{

    }
}

if USE_ANOTHER_ECS_FOR_RUNPY_DOCKER:
    default_docker = RELATE_DOCKERS["default"]
    default_docker["client_config"]["base_url"] = "http://119.23.140.116:2375"
    default_docker["local_docker_machine_config"]["enabled"] = False
    default_docker["execution_host_alias_dict"] = {"119.23.140.116": u"LearningWhat(ECS 10.29.248.41)"}

# Switch to turn on/off runpy, default to True. Setting this to False will
# Disable the functionality of Runpy code question. A critical check error
# will stop the server from start up unless you explicitly set
# "SILENCE_RUNPY_DOCKER_NOT_USABLE_ERROR" (below) to True.
#RELATE_RUNPY_DOCKER_ENABLED = True

# The config name which will be used for Runpy docker. If not set, "default" will
# be used.
# RELATE_RUNPY_DOCKER_CLIENT_CONFIG_NAME = "default"

# If True, submission of code question with RELATE_RUNPY_DOCKER_ENABLED = False
# won't send email notifications about RunpyDockerNotUsableError. Default to False
#SILENCE_RUNPY_DOCKER_NOT_USABLE_ERROR = False


# # Note: The following is used to ensure unittests can be run on Windows CI and for
# # backward compatibility, you should remove them in your local_settings.py if you
# # want to enable runpy docker functionality.
import sys
if sys.platform.startswith("win") or sys.platform.startswith("darwin"):
    SILENCE_RUNPY_DOCKER_NOT_USABLE_ERROR = True
    #RELATE_RUNPY_DOCKER_ENABLED = False

# }}}

# {{{ maintenance and announcements

RELATE_MAINTENANCE_MODE = False

RELATE_MAINTENANCE_MODE_EXCEPTIONS = []
# RELATE_MAINTENANCE_MODE_EXCEPTIONS = ["192.168.1.0/24"]

# May be set to a string to set a sitewide announcement visible on every page.
RELATE_SITE_ANNOUNCEMENT = None

# }}}

# Uncomment this to enable i18n, change 'en-us' to locale name your language.
# Make sure you have generated, translate and compile the message file of your
# language. If commented, RELATE will use default language 'en-us'.

#USE_I18N = True
#LANGUAGE_CODE = 'en-us'

# {{{ course specific language

# Whether enable course-specific language in course setup
RELATE_ENABLE_COURSE_SPECIFIC_LANG = True

# The allowed languages which can be used for rendering course view. Available
# COURSE_LANGUAGES can be found in django.conf.global_settings.COURSE_LANGUAGES.
# If not configured, django.conf.global_settings.COURSE_LANGUAGES will be used.

from django.utils.translation import ugettext_lazy as _

COURSE_LANGUAGES = [
    ('en', _('English')),
    ('zh-hans', _('Simplified Chinese')),
    ('de', _('German')),
]

# }}}

# {{{ exams and testing

# This may also be a callable that receives a local-timezone datetime and returns
# an equivalent dictionary.
#
# def RELATE_FACILITIES(now_datetime):
#     from relate.utils import localize_datetime
#     from datetime import datetime
#
#     if (now_datetime >= localize_datetime(datetime(2016, 5, 5, 0, 0))
#             and now_datetime < localize_datetime(datetime(2016, 5, 6, 0, 0))):
#         ip_ranges = [
#             "127.0.0.1/32",
#             "192.168.77.0/24",
#             ]
#     else:
#         ip_ranges = []
#
#     return {
#         "test_center": {
#             "ip_ranges": ip_ranges,
#             "exams_only": True,
#             },
#     }


RELATE_FACILITIES = {
    "test_center": {
        "ip_ranges": [
            "192.168.192.0/24",
            ],
        "exams_only": False,
    },
}

# For how many minutes is an exam ticket still usable for login after its first
# use?
RELATE_TICKET_MINUTES_VALID_AFTER_USE = 12*60

# }}}

# {{{ saml2 (optional)

if RELATE_SIGN_IN_BY_SAML2_ENABLED:
    from os import path
    import saml2.saml
    _BASEDIR = path.dirname(path.abspath(__file__))

    _BASE_URL = 'https://relate.cs.illinois.edu'

    # see saml2-keygen.sh in this directory
    _SAML_KEY_FILE = path.join(_BASEDIR, 'saml-config', 'sp-key.pem')
    _SAML_CERT_FILE = path.join(_BASEDIR, 'saml-config', 'sp-cert.pem')

    SAML_ATTRIBUTE_MAPPING = {
        'eduPersonPrincipalName': ('username',),
        'iTrustUIN': ('institutional_id',),
        'mail': ('email',),
        'givenName': ('first_name', ),
        'sn': ('last_name', ),
    }
    SAML_DJANGO_USER_MAIN_ATTRIBUTE = 'username'
    SAML_DJANGO_USER_MAIN_ATTRIBUTE_LOOKUP = '__iexact'

    SAML_CONFIG = {
        # full path to the xmlsec1 binary programm
        'xmlsec_binary': '/usr/bin/xmlsec1',

        # your entity id, usually your subdomain plus the url to the metadata view
        # (usually no need to change)
        'entityid': _BASE_URL + '/saml2/metadata/',

        # directory with attribute mapping
        # (already populated with samples from djangosaml2, usually no need to
        # change)
        'attribute_map_dir': path.join(_BASEDIR, 'saml-config', 'attribute-maps'),

        'allow_unknown_attributes': True,

        # this block states what services we provide
        'service': {
            'sp': {
                'name': 'RELATE SAML2 SP',
                'name_id_format': saml2.saml.NAMEID_FORMAT_TRANSIENT,
                'endpoints': {
                    # url and binding to the assertion consumer service view
                    # do not change the binding or service name
                    'assertion_consumer_service': [
                        (_BASE_URL + '/saml2/acs/',
                         saml2.BINDING_HTTP_POST),
                        ],
                    # url and binding to the single logout service view
                    # do not change the binding or service name
                    'single_logout_service': [
                        (_BASE_URL + '/saml2/ls/',
                         saml2.BINDING_HTTP_REDIRECT),
                        (_BASE_URL + '/saml2/ls/post',
                         saml2.BINDING_HTTP_POST),
                        ],
                    },

                # attributes that this project needs to identify a user
                'required_attributes': ['uid'],

                # attributes that may be useful to have but not required
                'optional_attributes': ['eduPersonAffiliation'],

                # in this section the list of IdPs we talk to are defined
                'idp': {
                    # Find the entity ID of your IdP and make this the key here:
                    'urn:mace:incommon:uiuc.edu': {
                        'single_sign_on_service': {
                            # Add the POST and REDIRECT bindings for the sign on service here:
                            saml2.BINDING_HTTP_POST:
                                'https://shibboleth.illinois.edu/idp/profile/SAML2/POST/SSO',
                            saml2.BINDING_HTTP_REDIRECT:
                                'https://shibboleth.illinois.edu/idp/profile/SAML2/Redirect/SSO',
                            },
                        'single_logout_service': {
                            # And the REDIRECT binding for the logout service here:
                            saml2.BINDING_HTTP_REDIRECT:
                            'https://shibboleth.illinois.edu/idp/logout.jsp',  # noqa
                            },
                        },
                    },
                },
            },

        # You will get this XML file from your institution. It has finite validity
        # and will need to be re-downloaded periodically.
        #
        # "itrust" is an example name that's valid for the University of Illinois.
        # This particular file is public and lives at
        # https://discovery.itrust.illinois.edu/itrust-metadata/itrust-metadata.xml

        'metadata': {
            'local': [path.join(_BASEDIR, 'saml-config', 'itrust-metadata.xml')],
            },

        # set to 1 to output debugging information
        'debug': 1,

        # certificate and key
        'key_file': _SAML_KEY_FILE,
        'cert_file': _SAML_CERT_FILE,

        'encryption_keypairs': [
                {
                    'key_file': _SAML_KEY_FILE,
                    'cert_file': _SAML_CERT_FILE,
                    }
                ],

        # own metadata settings
        'contact_person': [
            {'given_name': 'Andreas',
             'sur_name': 'Kloeckner',
             'company': 'CS - University of Illinois',
             'email_address': 'andreask@illinois.edu',
             'contact_type': 'technical'},
            {'given_name': 'Andreas',
             'sur_name': 'Kloeckner',
             'company': 'CS - University of Illinois',
             'email_address': 'andreask@illinois.edu',
             'contact_type': 'administrative'},
            ],
        # you can set multilanguage information here
        'organization': {
            'name': [('RELATE', 'en')],
            'display_name': [('RELATE', 'en')],
            'url': [(_BASE_URL, 'en')],
            },
        'valid_for': 24,  # how long is our metadata valid
        }

# }}}

# vim: filetype=python:foldmethod=marker
