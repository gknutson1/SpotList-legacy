from pydantic import BaseModel, Field


class Auth(BaseModel):
    user_id: str = Field(title="User ID", description="ID to identify the current user. Should be "
                                                      "passed into all further API calls as a header.")
    token: str = Field(description="Token to authenticate the user. Should be passed "
                                   "into all further API calls as a header.")
