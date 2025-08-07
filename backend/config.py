import multipart

MAX_FILE_SIZE = 2 * 1024 * 1024  # 2 MB file size limit

# Override python-multipart defaults
multipart.DEFAULT_MAX_FILE_SIZE = MAX_FILE_SIZE

# Override Starlette's formparser defaults
import starlette.formparsers as formparsers
formparsers.DEFAULT_MAX_FILE_SIZE = MAX_FILE_SIZE
formparsers.DEFAULT_MAX_FORM_MEMORY_SIZE = MAX_FILE_SIZE 