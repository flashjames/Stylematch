from storages.backends.s3boto import S3BotoStorage

class FakeFileObject(str):
    def startswith(self, not_needed):
        return False

class CustomS3BotoStorage(S3BotoStorage):
    """
    This is a hack that should be removed as fast as possible.
    See https://github.com/Jenso/ProjectX/issues/9
    """
    def path(self, name):
        fake_file_object = FakeFileObject("fakestring")
        return fake_file_object

    
