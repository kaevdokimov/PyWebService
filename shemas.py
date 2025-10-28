from datetime import datetime
from typing import Annotated, Optional

from pydantic import BaseModel, Field


class NewsSourceBase(BaseModel):
	name: Annotated[str, Field(..., title="Название источника", max_length=255)]
	url: Annotated[str, Field(..., title="URL источника", max_length=500)]
	description: Annotated[Optional[str], Field(None, title="Описание источника")] = None
	is_active: Annotated[bool, Field(..., title="Активность")] = True
	country: Annotated[str, Field("rus", title="Страна источника", max_length=10)] = "rus"


class NewsSourceCreate(NewsSourceBase):
	pass


class NewsSourceUpdate(NewsSourceBase):
	name: Annotated[str, Field(None, title="Название источника", max_length=255)] = None
	url: Annotated[str, Field(None, title="URL источника", max_length=500)] = None


class NewsSourceResponse(NewsSourceBase):
	id: Annotated[int, Field(..., title="ID источника")]
	created_at: Annotated[datetime, Field(..., title="Дата создания")]
	last_parsed_at: Annotated[Optional[datetime], Field(None, title="Дата последнего парсинга")] = None
	updated_at: Annotated[Optional[datetime], Field(None, title="Дата обновления")] = None

	class Config:
		from_attributes = True


class NewsSourceWithCount(NewsSourceResponse):
	news_count: Annotated[int, Field(..., title="Количество новостей")] = 0


class NewsItemBase(BaseModel):
	title: Annotated[str, Field(..., title="Заголовок новости", max_length=500)]
	description: Annotated[Optional[str], Field(None, title="Описание новости")] = None
	content: Annotated[Optional[str], Field(None, title="Содержимое новости")] = None
	link: Annotated[Optional[str], Field(None, title="Ссылка на новость", max_length=1000)] = None
	image_url: Annotated[Optional[str], Field(None, title="URL изображения", max_length=500)] = None
	guid: Annotated[str, Field(..., title="GUID новости", max_length=500)]
	published_at: Annotated[datetime, Field(..., title="Дата публикации")]


class NewsItemCreate(NewsItemBase):
	source_id: Annotated[int, Field(..., title="ID источника", gt=0)]


class NewsItemUpdate(NewsItemBase):
	title: Annotated[str, Field(None, title="Заголовок новости", max_length=500)] = None
	guid: Annotated[str, Field(None, title="GUID новости", max_length=500)] = None
	published_at: Annotated[datetime, Field(None, title="Дата публикации")] = None


class NewsItemResponse(NewsItemBase):
	id: Annotated[int, Field(..., title="ID новости")]
	source_id: Annotated[int, Field(..., title="ID источника")]
	created_at: Annotated[datetime, Field(..., title="Дата создания")]
	updated_at: Annotated[Optional[datetime], Field(None, title="Дата обновления")] = None

	class Config:
		from_attributes = True
