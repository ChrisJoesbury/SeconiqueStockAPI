# =============================================================================
# SeconiqueStockAPI | serializers.py
# =============================================================================
# DRF serializers for converting model instances to JSON. StockLevelsSerializer
# conditionally includes a company field for unscoped (admin) users who are not
# filtered to a single company.
# =============================================================================

#Get Rest Framework serializers
from rest_framework import serializers

#Get models for serialisation
from .models import StockLevels, GroupDescView, SubGroupDescView, RangeNameView


class StockLevelsSerializer(serializers.ModelSerializer):
    class Meta:
        model = StockLevels
        fields = ["partNum", "partDesc", "rangeName", "groupDesc", "subGroupDesc", "stockLev", "lastUpdatedDT"]
        ref_name = "stocklevels"

    def to_representation(self, instance):
        """Serialise a StockLevels instance, adding company for unscoped users.

        Args:
            instance (StockLevels): The model instance being serialised.

        Returns:
            dict: The serialised representation of the instance. A 'company'
                key is appended when the requesting user has no company_ID
                (i.e. admin or unscoped access); it is omitted for scoped users
                because all their records belong to a single company.

        Contract:
            - Reads request._cached_profile if already set by CompanyScopedMixin
              to avoid an extra database query per record.
            - Any exception during profile resolution is silently suppressed so
              that a serialisation failure never prevents data from being returned.
        """
        data = super().to_representation(instance)

        try:
            request = self.context.get('request') if self.context else None
            if request and hasattr(request, 'user'):
                user = getattr(request, 'user', None)
                if user and hasattr(user, 'id') and user.id is not None:
                    if not hasattr(request, '_cached_profile'):
                        try:
                            from .models import UserProfile
                            request._cached_profile = UserProfile.objects.select_related('user').get(user=user)
                        except UserProfile.DoesNotExist:
                            request._cached_profile = None
                        except Exception:
                            request._cached_profile = None

                    profile = getattr(request, '_cached_profile', None)
                    if profile is None or not profile.company_ID or not profile.company_ID.strip():
                        data['company'] = instance.company
        except Exception:
            pass

        return data


class GroupDescSerializer(serializers.ModelSerializer):
    class Meta:
        model = GroupDescView
        fields = ["groupDesc"]
        ref_name = "prodgroups"


class SubGroupDescSerializer(serializers.ModelSerializer):
    class Meta:
        model = SubGroupDescView
        fields = ["subGroupDesc"]
        ref_name = "prodsubgroups"


class RangeNameSerializer(serializers.ModelSerializer):
    class Meta:
        model = RangeNameView
        fields = ["rangeName"]
        ref_name = "ranges"
