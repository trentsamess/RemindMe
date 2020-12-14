from django.contrib.auth.base_user import BaseUserManager


class UserManager(BaseUserManager):
    def create_user(self, *args, **kwargs):
        if not kwargs.get('email'):
            raise ValueError('The email must be set')
        if not kwargs.get('password'):
            raise ValueError('Users must have a password')

        user = self.create(
            email=kwargs.get('email'),
            is_superuser=kwargs.get('is_superuser', False),
            is_active=True,
        )
        user.set_password(kwargs.get('password'))
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password, *args, **kwargs):
        user = self.create_user(
            email=self.normalize_email(email),
            password=password,
        )
        user.is_active = True
        user.save(using=self._db)
        return user
