#              M""""""""`M              dP
#              Mmmmmm   .M              88
#              MMMMP  .MMM   dP    dP   88  .dP    .d8888b.
#              MMP  .MMMMM   88    88   88888"     88'  `88
#              M' .MMMMMMM   88.  .88   88  `8b.   88.  .88
#              M         M   `88888P'   dP   `YP   `88888P'
#              MMMMMMMMMMM    -*-   Created by Zuko   -*-
#
#              * * * * * * * * * * * * * * * * * * * * *
#              * -    - -   F.R.E.E.M.I.N.D   - -    - *
#              * -  Copyright © 2025 (Z) Programing  - *
#              *    -  -  All Rights Reserved  -  -    *
#              * * * * * * * * * * * * * * * * * * * * *
class BaseAttributeModel:
    def __init__(self, *args, **kw):
        # super().__init__(*args, **kw, box_dots=True, box_default_box_create_on_get=True)
        pass

    def __getitem__(self, name):
        if isinstance(name, str):
            return getattr(self, name)

    def __setitem__(self, name, value):
        return setattr(self, name, value)

    def __delitem__(self, name):
        return delattr(self, name)

    def __contains__(self, name):
        """
        Check if attribute `name` is present in the object.
        Parameters
        ----------
        name : str
            The name of the attribute to check.
        Returns
        -------
        bool
            True if `name` is present, False otherwise.
        """
        return name in self.__dict__

    def get(self, name, default=None):
        return getattr(self, name, default)

    def set(self, name, value):
        return setattr(self, name, value)

    def unset(self, name):
        return delattr(self, name)
