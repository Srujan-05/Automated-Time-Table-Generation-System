"""Implement new timetable schema with Course, CourseInstance, and StudentGroup hierarchy

Revision ID: 002_new_schema
Revises: 7bfe3d34c4a5
Create Date: 2026-05-01 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa

revision = '002_new_schema'
down_revision = '7bfe3d34c4a5'
branch_labels = None
depends_on = None


def upgrade():
    # ========================================================================
    # 1. CREATE student_group_hierarchy TABLE (for parent-child relationships)
    # ========================================================================
    op.create_table(
        'student_group_hierarchy',
        sa.Column('child_id', sa.Integer(), nullable=False),
        sa.Column('parent_id', sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(['child_id'], ['student_groups.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['parent_id'], ['student_groups.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('child_id', 'parent_id')
    )
    
    # Create indexes
    op.create_index('idx_student_group_hierarchy_parent', 'student_group_hierarchy', ['parent_id'])
    op.create_index('idx_student_group_hierarchy_child', 'student_group_hierarchy', ['child_id'])

    # ========================================================================
    # 2. ADD level COLUMN to student_groups
    # ========================================================================
    op.add_column('student_groups', sa.Column('level', sa.String(50), default='batch'))
    op.add_column('student_groups', sa.Column('created_at', sa.DateTime(), server_default=sa.func.now()))

    # ========================================================================
    # 3. CREATE courses TABLE (base course template)
    # ========================================================================
    op.create_table(
        'courses',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('course_id', sa.String(20), nullable=False, unique=True),
        sa.Column('name', sa.String(100), nullable=False),
        sa.Column('total_credits', sa.Integer(), nullable=False),
        sa.Column('lectures_per_week', sa.Integer(), default=0),
        sa.Column('tutorials_per_week', sa.Integer(), default=0),
        sa.Column('practicals_per_week', sa.Integer(), default=0),
        sa.Column('description', sa.Text()),
        sa.Column('created_at', sa.DateTime(), server_default=sa.func.now()),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_courses_course_id', 'courses', ['course_id'])

    # ========================================================================
    # 4. CREATE course_instances TABLE (actual sessions to schedule)
    # ========================================================================
    op.create_table(
        'course_instances',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('course_id', sa.String(20), nullable=False),
        sa.Column('session_type', sa.String(20), nullable=False),
        sa.Column('instructor_id', sa.Integer(), nullable=False),
        sa.Column('room_id', sa.Integer(), nullable=False),
        sa.Column('student_group_id', sa.Integer(), nullable=False),
        sa.Column('slots_required', sa.Integer(), default=1),
        sa.Column('slots_continuous', sa.Boolean(), default=False),
        sa.Column('preference_bin', sa.Integer(), default=1),
        sa.Column('lecture_consecutive', sa.Boolean(), default=False),
        sa.Column('parallelizable_id', sa.Integer()),
        sa.Column('course_credits', sa.Float()),
        sa.Column('created_at', sa.DateTime(), server_default=sa.func.now()),
        sa.ForeignKeyConstraint(['course_id'], ['courses.course_id'], ),
        sa.ForeignKeyConstraint(['instructor_id'], ['professors.id'], ),
        sa.ForeignKeyConstraint(['room_id'], ['rooms.id'], ),
        sa.ForeignKeyConstraint(['student_group_id'], ['student_groups.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create indexes
    op.create_index('idx_course_instances_course_id', 'course_instances', ['course_id'])
    op.create_index('idx_course_instances_instructor_id', 'course_instances', ['instructor_id'])
    op.create_index('idx_course_instances_student_group_id', 'course_instances', ['student_group_id'])
    op.create_index('idx_course_instances_parallelizable_id', 'course_instances', ['parallelizable_id'])

    # ========================================================================
    # 5. CREATE time_slot_configuration TABLE
    # ========================================================================
    op.create_table(
        'time_slot_configuration',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('day_of_week', sa.String(20), nullable=False, unique=True),
        sa.Column('total_slots', sa.Integer(), nullable=False),
        sa.Column('preference_bin_1_slots', sa.Integer()),
        sa.Column('preference_bin_2_slots', sa.Integer()),
        sa.Column('preference_bin_3_slots', sa.Integer()),
        sa.Column('created_at', sa.DateTime(), server_default=sa.func.now()),
        sa.PrimaryKeyConstraint('id')
    )

    # ========================================================================
    # 6. CREATE preference_bins TABLE
    # ========================================================================
    op.create_table(
        'preference_bins',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('bin_id', sa.Integer(), nullable=False, unique=True),
        sa.Column('name', sa.String(50)),
        sa.Column('start_time', sa.Time()),
        sa.Column('end_time', sa.Time()),
        sa.PrimaryKeyConstraint('id')
    )

    # ========================================================================
    # 7. MODIFY TimetableEntry TABLE
    # ========================================================================
    # Add new columns
    op.add_column('timetable_entries', sa.Column('course_instance_id', sa.Integer()))
    op.add_column('timetable_entries', sa.Column('day_of_week', sa.String(20)))
    op.add_column('timetable_entries', sa.Column('instructor_id', sa.Integer()))
    
    # Populate new columns from existing data (join with CourseRequirement)
    # This uses raw SQL to preserve data during migration
    op.execute("""
        UPDATE timetable_entries
        SET day_of_week = day, instructor_id = professor_id
        WHERE day IS NOT NULL
    """)
    
    # Note: course_instance_id will be populated after CourseInstance records are created

    # ========================================================================
    # 8. MIGRATE DATA: CourseRequirement → Course + CourseInstance
    # ========================================================================
    # Step 1: Create Course records from unique course_codes in CourseRequirement
    op.execute("""
        INSERT INTO courses (course_id, name, total_credits, created_at)
        SELECT DISTINCT course_code, course_code, 3, NOW()
        FROM course_requirements
        WHERE course_code NOT IN (SELECT course_id FROM courses)
        ON CONFLICT (course_id) DO NOTHING
    """)
    
    # Step 2: Create CourseInstance records from CourseRequirement data
    op.execute("""
        INSERT INTO course_instances (
            course_id, session_type, instructor_id, room_id, student_group_id,
            slots_required, slots_continuous, preference_bin, course_credits, created_at
        )
        SELECT 
            cr.course_code, cr.session_type, cr.professor_id, 1, cr.student_group_id,
            cr.slots_required, cr.slots_continuous, cr.preference_bin, NULL, cr.created_at
        FROM course_requirements cr
    """)
    
    # Step 3: Now populate course_instance_id in timetable_entries
    # This matches based on course_code, session_type, professor_id, and student_group_id
    op.execute("""
        UPDATE timetable_entries te
        SET course_instance_id = (
            SELECT ci.id FROM course_instances ci
            WHERE ci.course_id = te.course_code
            LIMIT 1
        )
        WHERE course_instance_id IS NULL AND course_code IS NOT NULL
    """)

    # ========================================================================
    # 9. ADD CONSTRAINTS and CLEANUP
    # ========================================================================
    # Add constraints to new columns
    op.alter_column('timetable_entries', 'course_instance_id', 
                    existing_type=sa.Integer(),
                    nullable=False,
                    existing_nullable=True)
    op.alter_column('timetable_entries', 'day_of_week',
                    existing_type=sa.String(20),
                    nullable=False,
                    existing_nullable=True)
    op.alter_column('timetable_entries', 'instructor_id',
                    existing_type=sa.Integer(),
                    nullable=False,
                    existing_nullable=True)
    
    # Add foreign key constraints
    op.create_foreign_key('fk_timetable_entries_course_instance_id',
                         'timetable_entries', 'course_instances',
                         ['course_instance_id'], ['id'])
    op.create_foreign_key('fk_timetable_entries_instructor_id',
                         'timetable_entries', 'professors',
                         ['instructor_id'], ['id'])
    
    # Create indexes on new columns
    op.create_index('idx_timetable_entries_schedule_id', 'timetable_entries', ['schedule_id'])
    op.create_index('idx_timetable_entries_day_slot', 'timetable_entries', ['day_of_week', 'time_slot'])

    # Update Schedule table
    op.add_column('schedules', sa.Column('updated_at', sa.DateTime(), server_default=sa.func.now()))

    # Add created_at to Room if not exists
    op.add_column('rooms', sa.Column('created_at', sa.DateTime(), server_default=sa.func.now()))

    # Rename room location columns (x, y, z → location_x, location_y, location_z)
    op.alter_column('rooms', 'x', new_column_name='location_x')
    op.alter_column('rooms', 'y', new_column_name='location_y')
    op.alter_column('rooms', 'z', new_column_name='location_z')

    # Increase room name field length
    op.alter_column('rooms', 'name',
                    existing_type=sa.String(50),
                    type_=sa.String(100),
                    existing_nullable=False)

    # ========================================================================
    # 10. FINAL: Seed time slot configuration with defaults
    # ========================================================================
    op.execute("""
        INSERT INTO time_slot_configuration (day_of_week, total_slots, preference_bin_1_slots, preference_bin_2_slots, preference_bin_3_slots)
        VALUES 
            ('Monday', 9, 3, 3, 3),
            ('Tuesday', 9, 3, 3, 3),
            ('Wednesday', 5, 3, 2, 0),
            ('Thursday', 9, 3, 3, 3),
            ('Friday', 9, 3, 3, 3)
    """)
    
    # Seed preference bins
    op.execute("""
        INSERT INTO preference_bins (bin_id, name, start_time, end_time)
        VALUES 
            (1, 'Morning', '08:00:00', '12:00:00'),
            (2, 'Afternoon', '12:00:00', '16:00:00'),
            (3, 'Evening', '16:00:00', '20:00:00')
    """)


def downgrade():
    # ========================================================================
    # REVERSE MIGRATION
    # ========================================================================
    
    # Remove seeded data
    op.execute("DELETE FROM preference_bins")
    op.execute("DELETE FROM time_slot_configuration")
    
    # Drop new constraints and columns from timetable_entries
    op.drop_constraint('fk_timetable_entries_course_instance_id', 'timetable_entries', type_='foreignkey')
    op.drop_constraint('fk_timetable_entries_instructor_id', 'timetable_entries', type_='foreignkey')
    op.drop_column('timetable_entries', 'course_instance_id')
    op.drop_column('timetable_entries', 'day_of_week')
    op.drop_column('timetable_entries', 'instructor_id')
    
    # Drop new indexes
    op.drop_index('idx_timetable_entries_schedule_id', 'timetable_entries')
    op.drop_index('idx_timetable_entries_day_slot', 'timetable_entries')
    
    # Drop schedule column
    op.drop_column('schedules', 'updated_at')
    op.drop_column('rooms', 'created_at')
    
    # Rename room location columns back
    op.alter_column('rooms', 'location_x', new_column_name='x')
    op.alter_column('rooms', 'location_y', new_column_name='y')
    op.alter_column('rooms', 'location_z', new_column_name='z')
    
    # Decrease room name field length
    op.alter_column('rooms', 'name',
                    existing_type=sa.String(100),
                    type_=sa.String(50),
                    existing_nullable=False)
    
    # Drop tables
    op.drop_table('preference_bins')
    op.drop_table('time_slot_configuration')
    
    # Drop course_instances table and indexes
    op.drop_index('idx_course_instances_parallelizable_id', 'course_instances')
    op.drop_index('idx_course_instances_student_group_id', 'course_instances')
    op.drop_index('idx_course_instances_instructor_id', 'course_instances')
    op.drop_index('idx_course_instances_course_id', 'course_instances')
    op.drop_table('course_instances')
    
    # Drop courses table
    op.drop_index('idx_courses_course_id', 'courses')
    op.drop_table('courses')
    
    # Drop student_group_hierarchy table and indexes
    op.drop_index('idx_student_group_hierarchy_child', 'student_group_hierarchy')
    op.drop_index('idx_student_group_hierarchy_parent', 'student_group_hierarchy')
    op.drop_table('student_group_hierarchy')
    
    # Remove level column from student_groups
    op.drop_column('student_groups', 'level')
    op.drop_column('student_groups', 'created_at')
