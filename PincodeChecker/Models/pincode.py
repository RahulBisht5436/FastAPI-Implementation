from pydantic import BaseModel, StrictStr, field_validator


# ============================================================
# Request model for validating a single pincode
# ============================================================
class PincodeRequest(BaseModel):

    # StrictStr ensures that the pincode must be provided as a string.
    # For example: "110001" is valid, but 110001 (integer) is rejected.
    pincode: StrictStr

    # Pincode validation
    # This validator runs automatically whenever a PincodeRequest
    # object is created and validates the "pincode" field.
    @field_validator("pincode")
    @classmethod
    def validate_pincode(cls, value):

        # Check whether the pincode contains only numeric digits.
        # Example:
        # "110001" -> valid
        # "11000A" -> invalid
        if not value.isdigit():
            raise ValueError("Pincode must contain only digits")

        # Indian pincodes must contain exactly 6 digits.
        # Example:
        # "110001" -> valid
        # "11001"  -> invalid
        # "1100011" -> invalid
        if len(value) != 6:
            raise ValueError("Pincode must be exactly 6 digits")

        # Return the validated pincode.
        return value


# ============================================================
# Response model for location information
# ============================================================
class LocationResponse(BaseModel):

    # The 6-digit pincode associated with the location.
    pincode: str

    # Name of the city.
    city: str

    # Name of the state.
    state: str

    # Name of the district.
    district: str


# ============================================================
# Request model for validating multiple pincodes
# ============================================================
class BulkRequest(BaseModel):

    # List of pincodes that the client wants to search.
    #
    # StrictStr ensures that every item in the list must be
    # provided as a string.
    #
    # Example:
    # ["110001", "400001", "560001"]
    pincodes: list[StrictStr]

    # Validate the entire "pincodes" list.
    @field_validator("pincodes")
    @classmethod
    def validatePincodes(cls, values):

        # The API allows a minimum of 1 and a maximum of 20
        # pincodes in a single bulk request.
        #
        # Examples:
        # [] -> invalid
        # ["110001"] -> valid
        # 20 pincodes -> valid
        # 21 pincodes -> invalid
        if len(values) <= 0 or len(values) > 20:
            raise ValueError(
                "Length of the pincodes in Array can be 1-20 Only"
            )

        # Validate every pincode inside the list.
        for value in values:

            # Check that the pincode contains only digits.
            if not value.isdigit():
                raise ValueError(
                    "Pincode must contain only digits"
                )

            # Check that every pincode contains exactly 6 digits.
            if len(value) != 6:
                raise ValueError(
                    "Pincode must be exactly 6 digits"
                )

        # Return the validated list of pincodes.
        return values


# ============================================================
# Response model for bulk pincode lookup
# ============================================================
class BuldResponse(BaseModel):

    # Default response status.
    # If no value is provided, it will automatically be "success".
    status: str = "success"

    # Number of pincodes that were successfully found.
    found: int

    # Number of pincodes that were not found in the database.
    not_found: int

    # List containing location information for the pincodes
    # that were successfully found.
    pincodes: list[LocationResponse]