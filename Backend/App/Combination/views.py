# App/Combination/views.py
# import from framework
from django.shortcuts import render
from django.http import JsonResponse
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
# import from project
from .models import RouteXStation
from .serializers import RouteXStationSerializer, EditStationToRoute

@api_view(['GET'])
@permission_classes((IsAuthenticated,))
def route_seq_list(request):
    route_x_station = RouteXStation.objects.all()
    route_x_station_slzr = RouteXStationSerializer(instance=route_x_station, many=True)
    return JsonResponse(data=route_x_station_slzr.data, safe=False)

@api_view(['POST'])
def route_seq_create(request):
    route_x_station_slzr = EditStationToRoute(data=request.data)
    if route_x_station_slzr.is_valid():
        route_x_station_slzr.save()
        return JsonResponse(route_x_station_slzr.data, safe=False)
    else:
        return JsonResponse(route_x_station_slzr.errors)