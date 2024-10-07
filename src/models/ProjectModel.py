from .BaseDataModel import BaseDataModel
from .db_schemes import Project
from .enums import DataBaseEnum


# Project model to manage project collection:
class ProjectModel(BaseDataModel):
    # init takes db_client and pass it to parent.
    def __init__(self, db_client: object):
        super().__init__(db_client=db_client)

        # Access the collection:
        # it will be created in MongoDB if it does not already exist when a document is inserted.
        self.collection = self.db_client[DataBaseEnum.COLLECTION_PROJECT_NAME.value]

    # Third party create collection then Indexing:
    # because apply index on collection is done after init.
    # so we need to call function init_collection inside init.
    # but init_collection is motor functionality so it is async to call it we need await.
    # so we need init by async to call inside it with await, this is not acceptable async init.
    # so third party static method that apply outside the cls that init then init_collection.
    @classmethod
    async def create_instance(cls, db_client: object):
        instance = cls(db_client)
        await instance.init_collection()
        return instance

    # Apply indexes:
    async def init_collection(self):
        # get list of collections to search on project collection.
        # if not exist create one and apply indexing which created in the schema.
        all_collections = await self.db_client.list_collection_names()
        if DataBaseEnum.COLLECTION_PROJECT_NAME not in all_collections:
            self.collection = self.db_client[DataBaseEnum.COLLECTION_PROJECT_NAME.value]
            indexes = Project.get_indexes()
            for index in indexes:
                await self.collection.create_index(
                    keys=index["key"],
                    name=index["name"],
                    unique=index["unique"],
                )

    # Create projecy like insert a new field in collection:
    async def create_project(self, project: Project):
        # insert project instance as project scheme after convert to mongo formate "dict".
        # set _id "alias" and exlude the values defult like None "exclude _id" let mongo insert it not you with None.
        # motor async so await.
        result = await self.collection.insert_one(
            project.model_dump(by_alias=True, exclude_unset=True)
        )

        # Add _id to project by the actually created for it by mongo.
        # return the project instance.
        project.id = result.inserted_id
        return project

    # Get or Create project if not exist:
    async def get_or_create_project(self, project_id: str):
        # search on project based on project_id and get it as dict.
        record = await self.collection.find_one({"project_id": project_id})

        # if not exist, create instance as project scheme from project data.
        # pass project to be inserted in database.
        # return project instance.
        if record is None:
            project = Project(project_id=project_id)
            project = await self.create_project(project=project)
            return project

        # if exist, return project after convert to a project instance.
        return Project(**record)

    # Get all projects with paggination for handel scalabilities:
    async def get_all_projects(self, page: int = 1, page_size: int = 10):
        # 1. count projects
        # 2. Set them in pages to get total num of pages
        total_documents = await self.collection.count_documents({})
        total_pages = total_documents // page_size
        if total_documents % page_size > 0:
            total_pages += 1

        # 1. find without conditions
        # 2. skip past pages ((page - 1) * page_size)
        # 3. get at most page_size "a page"
        # 4. return cursur for memory efficent
        cursor = self.collection.find().skip((page - 1) * page_size).limit(page_size)

        # Get all projects but not memory efficent:
        # documents = list(cursor)

        # Using cursor:
        # cursor from motor so it is async.
        # found projects on this page and total num of pages.
        projects = []
        async for document in cursor:
            projects.append(Project(**document))
        return projects, total_pages
