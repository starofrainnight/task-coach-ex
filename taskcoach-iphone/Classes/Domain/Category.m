//
//  Category.m
//  TaskCoach
//
//  Created by Jérôme Laheurte on 14/01/09.
//  Copyright 2009 Jérôme Laheurte. See COPYING for details.
//

#import "Category.h"
#import "Database.h"
#import "Statement.h"
#import "Configuration.h"
#import "CategoriesSelector.h"
#import "String+Utils.h"

static Statement *_saveStatement = nil;

@implementation Category

@synthesize parentId;
@synthesize level;

- initWithId:(NSInteger)ID fileId:(NSNumber *)theFileId name:(NSString *)theName status:(NSInteger)theStatus taskCoachId:(NSString *)theTaskCoachId parentId:(NSNumber *)theParentId
{
	if (self = [super initWithId:ID fileId:theFileId name:theName status:theStatus taskCoachId:theTaskCoachId])
	{
		parentId = [theParentId retain];
		children = [[NSMutableArray alloc] init];
	}
	
	return self;
}

- (void)dealloc
{
	[parentId release];
	[children release];

	[super dealloc];
}

- (Statement *)saveStatement
{
	if (!_saveStatement)
		_saveStatement = [[[Database connection] statementWithSQL:[NSString stringWithFormat:@"UPDATE %@ SET fileId=?, name=?, status=?, taskCoachId=?, parentId=? WHERE id=?", [self class]]] retain];
	return _saveStatement;
}

- (void)bindId
{
	[[self saveStatement] bindInteger:objectId atIndex:6];
}

- (void)bind
{
	[super bind];
	
	if (parentId)
		[[self saveStatement] bindInteger:[parentId intValue] atIndex:5];
	else
		[[self saveStatement] bindNullAtIndex:5];
}

- (NSInteger)countForTable:(NSString *)tableName
{
	NSMutableArray *where = [[NSMutableArray alloc] initWithCapacity:2];
	
	if (![Configuration configuration].showCompleted)
		[where addObject:@"completionDate IS NULL"];

	CategoriesSelector *sel = [[CategoriesSelector alloc] initWithId:objectId];
	[where addObject:[sel clause]];
	[sel release];
	
	[[[Database connection] statementWithSQL:[NSString stringWithFormat:@"SELECT COUNT(*) AS total FROM %@ LEFT JOIN TaskHasCategory ON id=idTask WHERE %@", tableName, [@" AND " stringByJoiningStrings:where]]] execWithTarget:self action:@selector(setCount:)];

	return taskCount;
}

- (void)setCount:(NSDictionary *)dict
{
	taskCount = [[dict objectForKey:@"total"] intValue];
}

- (void)addChild:(Category *)child
{
	[children addObject:child];
}

- (void)finalizeChildren:(NSMutableArray *)categories
{
	[categories addObject:self];
	[self release];
	
	for (Category *child in children)
	{
		child.level = level + 1;
		[child finalizeChildren:categories];
	}
	
	[children release];
	children = nil;
}

- (void)removeAllTasks
{
	Statement *req = [[Database connection] statementWithSQL:@"DELETE FROM TaskHasCategory WHERE idCategory=?"];
	[req bindInteger:objectId atIndex:1];
	[req exec];
}

@end
