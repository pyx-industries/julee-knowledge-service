import logging
from typing import List, Optional
from uuid import UUID

try:
    import knowledge_service.domain as domain
    import knowledge_service.repositories as repositories
    from knowledge_service.django_setup import setup_django
    from knowledge_service.repositories import DumbRepo as Repository  # FIXME
except ModuleNotFoundError:
    from django_setup import setup_django

    import domain
    import repositories
    from repositories import DumbRepo as Repository  # FIXME

setup_django()

from django.apps import apps  # NOQA
from django.contrib.auth.models import User as DjangoUser  # NOQA
from django.core.exceptions import ObjectDoesNotExist  # NOQA
from django.core.files.base import ContentFile  # NOQA
from django.db import IntegrityError  # NOQA
from django.db import transaction  # NOQA

# django_setup.setup_django()
# the docker-composition mounts this at /app/julee_django/
# os.environ.setdefault("DJANGO_SETTINGS_MODULE", "julee_django.julee.settings")
# # the django stuff assumes relative imports from julee_django/
# sys.path.append(
#     os.path.abspath(
#         os.path.join(
#             os.path.dirname(os.path.abspath(__file__)), "julee_django/"
#         )
#     )
# )
# #django.setup()


# these would otherwise be regular from app.models import Foo
# but using the django model registry is nicer
# than further poluting the sys.path
Organisation = apps.get_model("core", "Organisation")
Subscription = apps.get_model("knowledge", "Subscription")
Collection = apps.get_model("knowledge", "Collection")
Resource = apps.get_model("knowledge", "Resource")
ResourceType = apps.get_model("knowledge", "ResourceType")

# TODO: use this more rigorously (debug log, info log, etc)
logger = logging.getLogger(__name__)


class CeleryTaskDispatchRespository(repositories.TaskDispatchRepository):
    def initiate_processing_of_new_resource(self, resource_id: str) -> None:
        # need to do this in here to avoid circular imports
        # maybe avoided by splitting the modules?
        import worker

        worker.initiate_processing_of_new_resource.apply_async(
            kwargs={"resource_id": resource_id}
        )
        return None

    def send_quarantine_notification(self, resource_id: str) -> None:
        import worker

        worker.send_quarantine_notification.apply_async(
            kwargs={"resource_id": resource_id}
        )
        return None

    def send_validation_error_notification(self, resource_id: str) -> None:
        import worker

        worker.send_validation_error_notification.apply_async(
            kwargs={"resource_id": resource_id}
        )
        return None

    def initiate_resource_graph(self, resource_id: str) -> None:
        import worker

        worker.initiate_resource_graph.apply_async(
            kwargs={"resource_id": resource_id}
        )
        return None

    def extract_plain_text_of_resource(self, resource_id: str) -> None:
        import worker

        worker.extract_plain_text_of_resource.apply_async(
            kwargs={"resource_id": resource_id}
        )
        return None

    def chunk_resource_text(self, resource_id: str) -> None:
        import worker

        worker.chunk_resource_text.apply_async(
            kwargs={"resource_id": resource_id}
        )
        return None

    def update_chunks_with_embeddings(self, resource_id: str) -> None:
        import worker

        worker.update_chunks_with_embeddings.apply_async(
            kwargs={"resource_id": resource_id}
        )
        return None

    def ventilate_resource_processing(self, resource_id: str) -> None:
        import worker

        worker.ventilate_resource_processing.apply_async(
            kwargs={"resource_id": resource_id}
        )
        return None


class DjangoCollectionRepository(repositories.CollectionRepository):
    # probably want a resource_type_ids: list
    def delete_collection(self, collection_id: str):
        num_found = Collection.objects.filter(
            id=UUID(str(collection_id))
        ).count()
        if num_found != 1:
            return False
        else:
            c = Collection.objects.get(pk=UUID(str(collection_id)))
            c.delete()
            return True

    def create_new_collection(
        self,
        name: str,
        subscription_id: str,
        description: Optional[str],
        resource_type_ids: List[str],
    ):
        resource_type_ids = [
            UUID(resource_id) for resource_id in resource_type_ids
        ]
        collection = Collection(
            name=name, subscription_id=subscription_id, description=description
        )

        try:
            collection.save()
        except IntegrityError as e:
            logger.error(f"Error creating collecion: {e}")
            raise e

        try:
            resource_types = ResourceType.objects.filter(
                id__in=resource_type_ids
            )
            collection.resource_types.set(resource_types)
            collection.save()
        except Exception as e:
            logger.error(f"Error associating resource types: {e}")
            raise e

        return domain.Collection(
            id=str(collection.id),
            name=collection.name,
            subscription_id=subscription_id,
            description=collection.description,
            resource_type_ids=[
                str(rt.id) for rt in collection.resource_types.all()
            ],
        )

    def get_collection_by_subscription_and_name(
        self, subscription_id=None, name=None
    ):
        try:
            c = Collection.objects.filter(
                name=name, subscription_id=subscription_id
            ).all()[0]
            return domain.Collection(
                id=str(c.id),
                name=name,
                subscription_id=subscription_id,
                resource_type_ids=[str(rt.id) for rt in c.resource_types.all()],
                description=c.description,
            )
        except Exception:
            return None

    def get_collection_by_id(self, collection_id: UUID):
        found = Collection.objects.get(pk=collection_id)
        if found:
            return domain.Collection(
                id=str(found.id),
                name=found.name,
                subscription_id=found.subscription_id,
                resource_type_ids=[
                    str(rt.id) for rt in found.resource_types.all()
                ],
                description=found.description,
            )
        return None


class DjangoResourceTypeRepository(repositories.ResourceTypeRepository):
    def get_resource_type_by_id(self, resource_type_id):
        if ResourceType.objects.filter(id=resource_type_id).count() != 1:
            return None
        rt = ResourceType.objects.get(pk=UUID(str(resource_type_id)))
        return domain.ResourceType(id=rt.id, name=rt.name, tooltip=rt.tooltip)

    def get_resource_type_list(self):
        return [
            domain.ResourceType(id=str(rt.id), name=rt.name, tooltip=rt.tooltip)
            for rt in ResourceType.objects.all()
        ]


class DjangoResourceRepository(repositories.ResourceRepository):
    def get_resource_list(self):  # do we really need this?
        resources = []
        for r in Resource.objects.all():
            resources.append(
                domain.Resource(
                    id=str(r.id),
                    collection_id=str(r.collection.id),
                    resource_type_id=str(r.resource_type.id),
                    file_name=r.file_name,
                    name=r.name,
                    file_type=r.file_type,
                    file=None,  # fixme
                    metadata_file=None,  # fixme
                )
            )
        return resources

    def get_resource_list_for_collection(self, collection_id):
        resources = []
        for r in Resource.objects.filter(
            collection_id=UUID(collection_id)
        ).all():
            resources.append(
                domain.Resource(
                    id=str(r.id),
                    collection_id=str(collection_id),
                    resource_type_id=str(r.resource_type.id),
                    file_name=r.file_name,
                    name=r.name,
                    file_type=r.file_type,
                    file=None,  # fixme
                    metadata_file=None,  # fixme
                )
            )
        return resources

    def get_resource_by_id(self, resource_id: UUID):
        found = Resource.objects.get(pk=resource_id)
        if found:
            file_content = found.file.read() if found.file else None
            metadata_file_content = (
                found.metadata_file.read() if found.metadata_file else None
            )
            return Resource(
                id=str(found.id),
                collection_id=str(found.collection.id),
                resource_type_id=str(found.resource_type.id),
                name=found.name,
                file_name=found.file_name,
                file_type=found.file_type,
                file=file_content,
                metadata_file=metadata_file_content,
            )
        return None

    def set_file_type_for_resource_id(
        self, resource_id: str, file_type: str
    ) -> Optional[domain.Resource]:
        found = Resource.objects.get(pk=UUID(str(resource_id)))
        if found:
            found.file_type = file_type
            found.save()
            return Resource(
                id=str(found.id),
                collection_id=str(found.collection.id),
                resource_type_id=str(found.resource_type.id),
                name=found.name,
                file_name=found.file_name,
                file_type=found.file_type,
                file=found.file,
                metadata_file=found.metadata_file,
            )
        return None

    @transaction.atomic
    def update_resource(self, resource: domain.Resource) -> domain.Resource:
        """Update an existing resource if different from current state.

        Args:
            resource: The resource object with updated values

        Returns:
            domain.Resource: Updated resource domain model

        Raises:
            ObjectDoesNotExist: If resource_id doesn't exist
        """
        found = Resource.objects.get(pk=UUID(str(resource.id)))

        # Check if anything has changed
        current_state = domain.Resource(
            id=str(found.id),
            collection_id=str(found.collection.id),
            resource_type_id=str(found.resource_type.id),
            name=found.name,
            file_name=found.file_name,
            file_type=found.file_type,
            file=found.file.read() if found.file else None,
            metadata_file=found.metadata_file.read() if found.metadata_file else None,
        )

        # Return current state if no changes
        if current_state == resource:
            return current_state

        # Update fields that can change
        found.name = resource.name
        found.file_type = resource.file_type

        # Handle file content updates
        if resource.file is None:
            # Clear the file if None
            found.file = None
        elif found.file:
            # Only update if content different
            if found.file.read() != resource.file:
                found.file.delete()
                found.file = ContentFile(resource.file, resource.file_name)
        else:
            # No existing file, add new one
            found.file = ContentFile(resource.file, resource.file_name)

        found.save()

        # Return fresh copy from DB to ensure consistency
        return self.get_resource_by_id(resource.id)

    def create_new_resource(
        self,
        collection_id: str,
        resource_type_id: str,
        name: str,
        file_name: str,
        file_content: bytes,
        webhooks: tuple,
        # metadata: str
    ):
        try:
            resource_type = ResourceType.objects.get(
                pk=UUID(str(resource_type_id))
            )
        except ObjectDoesNotExist:
            raise ValueError("ResourceType does not exist")
        try:
            collection = Collection.objects.get(pk=UUID(str(collection_id)))
        except ObjectDoesNotExist:
            raise ValueError("Collection does not exist")

        file_content_object = ContentFile(file_content, file_name)
        resource = Resource(
            collection=collection,
            resource_type=resource_type,
            file_name=file_name,
            name=name,
            file=file_content_object,
            # metadata=str(metadata),
            # webhooks=str(webhooks), # FIXME
            # should these be entities, and callbacks too?
        )
        resource.save()
        return domain.Resource(
            id=str(resource.id),
            collection_id=str(resource.collection.id),
            resource_type_id=str(resource.resource_type.id),
            name=resource.name,
            file_name=resource.file_name,
            file_type=resource.file_type,
            file=resource.file,
            metadata_file=resource.metadata_file,
        )

    def count_resources_in_collection(self, collection_id: str) -> int:
        """Count number of resources in a collection using Django ORM

        Args:
            collection_id: ID of the collection

        Returns:
            Number of resources in the collection
        """
        return Resource.objects.filter(collection_id=UUID(str(collection_id))).count()


class DjangoSubscriptionRepository(repositories.SubscriptionRepository):
    def get_subscription_list(self):
        subscriptions = []
        for s in Subscription.objects.all():
            subscriptions.append(
                domain.Subscription(
                    id=str(s.id),
                    is_active=s.is_active,
                    name=s.name,
                    resource_types=[
                        domain.ResourceType(
                            id=str(rt.id), name=rt.name, tooltip=rt.tooltip
                        )
                        for rt in s.resource_types.all()
                    ],
                    collections=[
                        domain.Collection(
                            id=str(c.id),
                            name=c.name,
                            description=c.description,
                            subscription_id=str(s.id),
                            resource_type_ids=[
                                str(rt.id) for rt in c.resource_types.all()
                            ],
                        )
                        for c in s.collections.all()
                    ],
                )
            )
        return subscriptions

    def get_subscription_details(self, subscription_id):
        try:
            s = Subscription.objects.get(pk=subscription_id)
            return domain.Subscription(
                id=str(s.id),
                name=s.name,
                is_active=s.is_active,
                collections=[
                    domain.Collection(
                        id=str(c.id),
                        name=c.name,
                        subscription_id=str(s.id),
                        resource_type_ids=[
                            str(rt.id) for rt in c.resource_types.all()
                        ],
                    )
                    for c in s.collections.all()
                ],
                resource_types=[
                    domain.ResourceType(
                        id=str(rt.id), name=rt.name, tooltip=rt.tooltip
                    )
                    for rt in s.resource_types.all()
                ],
            )
        except Subscription.DoesNotExist:
            return None

    def delete_subscription(self, subscription_id):
        try:
            subscription = Subscription.objects.get(pk=subscription_id)
            subscription.delete()
            return True
        except Subscription.DoesNotExist:
            return False

    def create_new_subscription(
        self, name: str, resource_type_ids: list, status: str
    ):
        try:
            for rtid in resource_type_ids:
                num_found = ResourceType.objects.filter(
                    id=UUID(str(rtid))
                ).count()
                assert num_found == 1
        except AssertionError:
            raise Exception(
                "Unable to create new subscription "
                f"with non-existant resource_type '{rtid}'"
            )
        resource_type_ids = [
            UUID(resource_id) for resource_id in resource_type_ids
        ]
        subscription = Subscription(
            name=name,
            is_active=True if status == "active" else False,
        )
        try:
            subscription.save()
        except IntegrityError as e:
            logger.error(f"Error creating subscription: {e}")
            raise e
        try:
            resource_types = ResourceType.objects.filter(
                id__in=resource_type_ids
            )
            subscription.resource_types.set(resource_types)
            subscription.save()
        except Exception as e:
            logger.error(f"Error associating resource types: {e}")
            raise e
        return domain.Subscription(
            id=str(subscription.id),
            is_active=subscription.is_active,
            name=subscription.name,
            collections=[],
            resource_types=[
                domain.ResourceType(
                    id=str(rt.id), name=str(rt.name), tooltip=str(rt.tooltip)
                )
                for rt in subscription.resource_types.all()
            ],
        )


 # Django-based User repository
class DjangoUserRepository(Repository):
    def get_resource_types_for_collection(self, collection_id):
        c = Collection.objects.get(id=collection_id)
        return [
            domain.ResourceType(id=str(rt.id), name=rt.name, tooltip=rt.tooltip)
            for rt in c.resource_types.all()
        ]

    def list_users(self):
        # TODO - fix me first
        users = []
        for u in DjangoUser.objects.all():
            users.append(
                domain.User(
                    id=u.id,
                    username=u.username,
                    email=u.email,
                    password=u.password,  # make that optional!
                )
            )
        return users

    def create(self, username: str, email: str, password: str) -> domain.User:
        pass

    def get_by_id(self, user_id: int) -> domain.User:
        pass

    def update(
        self, user_id: int, username: str, email: str, password: str
    ) -> domain.User:
        pass

    def delete(self, user_id: int) -> None:
        pass


# Django-based Organisation repository
class DjangoOrganisationRepository(Repository):
    def create(
        self, name: str, description: Optional[str] = None
    ) -> domain.Organisation:
        pass

    def get_by_id(self, organisation_id: int) -> domain.Organisation:
        pass

    def delete(self, organisation_id: int) -> None:
        pass

    def update(
        self, name: str, description: Optional[str]
    ) -> domain.Organisation:
        pass


 # # Django-based Domain repository
 # class DjangoDomainRepository(Repository):
 #     def create(
 #         self,
 #         name: str,
 #         description: Optional[str] = None,
 #         user_id: Optional[int] = None,
 #         organisation_id: Optional[int] = None,
 #     ) -> domain.Domain:
 #         pass

 #     def get_by_id(self, domain_id: int) -> domain.Domain:
 #         pass

 #     def delete(self, organisation_id: int) -> None:
 #         pass

 #     def update(
 #         self, name: str, description: Optional[str]
 #     ) -> domain.Organisation:
 #         pass
