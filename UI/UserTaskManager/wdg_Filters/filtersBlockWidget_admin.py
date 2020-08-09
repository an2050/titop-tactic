from .FiltersBlockWidget import FiltersBlockWidget


class FiltersBlockWidget_admin(FiltersBlockWidget):
    def __init__(self, taskManagerWdg):
        super(FiltersBlockWidget_admin, self).__init__(taskManagerWdg)

        self.filterUser_blockWidget.setVisible(False)
