import datetime

from pydantic import BaseModel

class Account(BaseModel):
    id: str
    displayName: str
    name: str
    email: str
    failedLoginAttempts: int
    lastLogin: datetime.datetime
    numberOfDisplayNameChanges: int
    ageGroup: str
    headless: bool
    country: str
    lastName: str
    preferredLanguage: str
    lastDisplayNameChange: datetime.datetime
    canUpdateDisplayName: bool
    tfaEnabled: bool
    emailVerified: bool
    minorVerified: bool
    minorExpected: bool
    minorStatus: str
    cabinedMode: bool
    hasHashedEmail: bool


class PastSeason(BaseModel):
    seasonNumber: int
    numWins: int
    numHighBracket: int
    numLowBracket: int
    seasonXp: int
    seasonLevel: int
    bookXp: int
    bookLevel: int
    purchasedVIP: bool
    numRoyalRoyales: int

class AttributesStats(BaseModel):
    lifetime_wins: int
    past_seasons: list[PastSeason] = []

class Stats(BaseModel):
    attributes: AttributesStats



class FortniteAccount(BaseModel):
    created: datetime.datetime
    updated: datetime.datetime
    accountId: str
    stats: Stats





class Item(BaseModel):
    id: str
    type_: str
    item_seen: bool = False