import os
import sys

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "julee_django.julee.settings")
# sigh, and everything else
sys.path.append(
    os.path.abspath(
        os.path.join(
            os.path.dirname(os.path.abspath(__file__)), "../julee_django"
        )
    )
)
# raise Exception(f"DEBUG: {sys.path}")

# these must come from knowledge_service/, not julee_django/knowledge_service.
try:
    import knowledge_service.django_repository as django_repo
    import knowledge_service.neo4j_repository as neo4j_repo
    from knowledge_service.config_management import RepoSet
except ModuleNotFoundError:
    import django_repository as django_repo
    import neo4j_repository as neo4j_repo
    from config_management import RepoSet
# import your filth here, and do the shameful things you must
# to ensure your concrete repositories instantiate sucessfully.
#
# sigh, django


#
# now populate the reposet,
# where the dirty code is actually wired-in
#
reposet = RepoSet()
reposet["task_dispatch_repository"] = (
    django_repo.CeleryTaskDispatchRespository()
)
reposet["subscription_repository"] = django_repo.DjangoSubscriptionRepository()
reposet["resource_repository"] = django_repo.DjangoResourceRepository()
reposet["collection_repository"] = django_repo.DjangoCollectionRepository()
reposet["resource_type_repository"] = django_repo.DjangoResourceTypeRepository()
reposet["graph_repository"] = neo4j_repo.Neo4jGraphRepository()
