import re
from typing import Union

class CoordinateValidator:
    """Class responsible for validating geographical coordinates (Latitude and Longitude)."""

    # Expresiones regulares para validar el formato de texto antes de la conversión a float
    LATITUDE_REGEX = r"^[-+]?([1-8]?\d(\.\d+)?|90(\.0+)?)$"
    LONGITUDE_REGEX = r"^[-+]?(180(\.0+)?|((1[0-7]\d)|([1-9]?\d))(\.\d+)?)$"

    @classmethod
    def is_informed(val):
        return val is not None and str(val).strip() != ""
    
    @classmethod
    def validate_latitude(cls, lat: Union[int, float, str]) -> bool:
        """
        Validates if a value is a valid latitude (-90 to 90).
        Accepts floats, ints, or strings that can be converted to float.
        """
        if lat is None:
            return False
            
        if isinstance(lat, str):
            lat = lat.strip()
            if not re.match(cls.LATITUDE_REGEX, lat):
                return False
            
        try:
            lat_float = float(lat)
            return -90 <= lat_float <= 90
        except (ValueError, TypeError):
            return False

    @classmethod
    def validate_longitude(cls, lng: Union[int, float, str]) -> bool:
        """
        Validates if a value is a valid longitude (-180 to 180).
        Accepts floats, ints, or strings that can be converted to float.
        """
        if lng is None:
            return False

        if isinstance(lng, str):
            lng = lng.strip()
            if not re.match(cls.LONGITUDE_REGEX, lng):
                return False

        try:
            lng_float = float(lng)
            return -180 <= lng_float <= 180
        except (ValueError, TypeError):
            return False

    @classmethod
    def validate_coordinates(cls, lat: Union[int, float, str], lng: Union[int, float, str]) -> bool:
        """Validates a pair of coordinates (latitude and longitude) simultaneously."""
        return cls.validate_latitude(lat) and cls.validate_longitude(lng)
