from api.models import User, ClassRoom

classes = ['CPE 500L', 'CPE 400L', 'CPE 300L', 'CPE 200L', 'CPE 100L']

queryset = [ClassRoom.objects.create(name=classroom) for classroom in classes]
