from .game_engine import Level

__walls__ = {
    'empty': [],
    'reverse_a': [
        (0, 6), (1, 6), (2, 6), (3, 6), (4, 6), (5, 6), (6, 6),
        (0, 5), (3, 5), (6, 5),
        (0, 4), (3, 4), (6, 4),
        (0, 3), (6, 3),
        (0, 2), (3, 2), (6, 2),
        (0, 1), (6, 1),
        (0, 0), (1, 0), (2, 0), (3, 0), (4, 0), (5, 0), (6, 0)
    ],
    'circle': [
        (0, 6), (1, 6), (2, 6), (3, 6), (4, 6), (5, 6), (6, 6),
        (0, 5), (6, 5),
        (0, 4), (6, 4),
        (0, 3), (6, 3),
        (0, 2), (6, 2),
        (0, 1), (6, 1),
        (0, 0), (1, 0), (2, 0), (3, 0), (4, 0), (5, 0), (6, 0)
    ],
    'o': [
        (0, 6), (1, 6), (2, 6), (3, 6), (4, 6), (5, 6), (6, 6),
        (0, 5), (6, 5),
        (0, 4), (6, 4),
        (0, 3), (3, 3), (6, 3),
        (0, 2), (6, 2),
        (0, 1), (6, 1),
        (0, 0), (1, 0), (2, 0), (3, 0), (4, 0), (5, 0), (6, 0)
    ]
}

LEVELS = [
    Level(
        field_size=(5, 5),
        player=(0, 0),
        walls=__walls__['empty'],
        boxes=[(1, 1), (3, 3)],
        goal=(4, 4),
        max_points=20
    ),
    Level(
        field_size=(7, 7),
        player=(2, 4),
        walls=__walls__['circle'],
        boxes=[(4, 2)],
        goal=(5, 5),
        max_points=30
    ),
    Level(
        field_size=(7, 7),
        player=(4, 5),
        walls=__walls__['circle'],
        boxes=[(4, 2), (2, 4)],
        goal=(2, 1),
        max_points=40
    ),
    Level(
        field_size=(7, 7),
        player=(2, 4),
        walls=__walls__['o'],
        boxes=[(3, 2)],
        goal=(2, 5),
        max_points=50
    ),
    Level(
        field_size=(7, 7),
        player=(2, 4),
        walls=__walls__['o'],
        boxes=[(2, 3), (4, 2)],
        goal=(5, 5),
        max_points=60
    ),
    Level(
        field_size=(7, 7),
        player=(1, 4),
        walls=__walls__['reverse_a'],
        boxes=[(2, 3), (4, 2)],
        goal=(4, 4),
        max_points=70
    ),
    Level(
        field_size=(7, 7),
        player=(2, 4),
        walls=__walls__['reverse_a'],
        boxes=[(2, 3), (2, 2)],
        goal=(4, 5),
        max_points=80
    )
]
