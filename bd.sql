-- Сортировка
select * from students
order by code_stud;

select name_lector, post, science from lectors
order by post asc, science desc;

select name_group, num_course from groups_
order by num_course desc;

-- Изменение порядка следования полей
select code_group, name, surname, lastname, phone, birthday from students;

select name_subject, code_subject from subjects;

-- Выбор некоторых полей из двух таблиц
select s.surname, s.name, s.lastname, g.name_group from students s 
join groups_ g on s.code_group = g.code_group;

select p.date_exam, l.name_lector from progress p
join lectors l on p.code_lector = l.code_lector;

select p.date_exam, s.name_subject from progress p
join subjects s on p.code_subject = s.code_subject;

-- Условие неточного совпадения
select name_lector from lectors
where science like 'К%';

select s.surname, s.name, s.lastname, g.name_group from students s
join groups_ g on s.code_group = g.code_group
where g.name_group like 'АС%';

select name_subject from subjects
where name_subject like 'Математ%';

-- Точное несовпадение значений одного из полей
select name_lector, post from lectors
where science != 'д.т.н.';

select name_group from groups_
where name_speciality != 'Электротехника';

select * from subjects
where name_subject != 'Высшая математика';

-- Выбор записей по диапазону значений (Between)
select p.date_exam, s.name_subject from progress p
join subjects s on p.code_subject = s.code_subject
where p.date_exam between '2003-01-01' and '2003-02-01';

select name_lector, post from lectors
where date_ between '2000-03-12' and '2000-06-15';

select surname, name, lastname, phone from students
where phone between 220000 and 226666;

select name_subject from subjects
where name_subject between 'В%' and 'Г%';

-- Выбор записей по диапазону значений (In)
select g.name_group, g.name_speciality from groups_ g 
join students s on g.code_group = s.code_group 
where s.code_stud in ('АС-12-02', 'ПИ-14-03', 'АС-21-03', 'БИ-12-02');

select name_lector, post from lectors
where science in ('к.т.н.', 'к.э.н.', 'д.т.н.');

select s.surname, s.name, s.lastname from students s
join progress p on s.code_stud = p.code_stud
where p.code_subject in (5, 8, 12, 25);

-- Выбор записей с использованием Like
select name_subject from subjects
where name_subject like 'М%';

select surname, name, lastname, birthday from students
where surname like '%Нова%';

select name_group from groups_ 
where name_group like '%0';

-- Выбор записей по нескольким условиям
select s.surname, s.name, s.code_group from students s
join progress p on s.code_stud = p.code_stud
join subjects sub on p.code_subject = sub.code_subject
where sub.name_subject = 'Математический анализ';

select distinct l.name_lector from lectors l
join progress p on l.code_lector = p.code_lector
where p.code_subject between 5 and 12
and p.date_exam between '2003-01-01' and '2003-02-01';

select g.name_group, g.num_course from groups_ g 
join students s on g.code_group = s.code_group 
where s.birthday between '1976-01-01' and '1978-01-01' 
and s.code_stud between '10' and '150';

-- Многотабличные запросы (выборка из двух таблиц, выборка из трех таблиц с использованием JOIN)
select distinct s.name_subject, l.name_lector from subjects s 
join progress p on s.code_subject = p.code_subject 
join lectors l on p.code_lector = l.code_lector;

select s.surname, s.name, g.num_course from students s 
join groups_ g on s.code_group = g.code_group 
where g.name_group = 'Ас-31';

select distinct l.name_lector from lectors l 
join progress p on l.code_lector = p.code_lector 
join students s on p.code_stud = s.code_stud 
where s.code_group in (10, 12, 15);

select distinct s.name_subject, l.name_lector from subjects s 
join progress p on s.code_subject = p.code_subject 
join lectors l on p.code_lector = l.code_lector 
where p.date_exam between '2003-01-15' and '2003-02-16';

-- Вычисления
select name_lector, science, extract(year from age(date_)) as years_worked from lectors;

select surname, name, lastname, extract(year from age(birthday)) as age from students;

select s.surname, s.name, s.lastname, g.num_course, (4 - g.num_course) as years_left 
from students s 
join groups_ g on s.code_group = g.code_group;

-- Вычисление итоговых значений с использованием агрегатных функций
select g.name_group, count(s.code_stud) as count_students from groups_ g 
join students s on g.code_group = s.code_group
group by g.name_group;

select s.surname, s.name, avg(p.estimate) as avg_estimate from students s
join progress p on s.code_stud = p.code_stud
where p.date_exam between '2003-01-05' and '2003-01-25' group by s.surname, s.name;

select s.surname, s.name from students s
join progress p on s.code_stud = p.code_stud
group by s.surname, s.name
having avg(p.estimate) = (select max(avg_estimate)
from (select avg(estimate) as avg_estimate
from progress
group by code_stud) as subquery);

select * from lectors
where date_ = (select min(date_) from lectors);

-- Изменение наименований полей
select g.name_group, count(s.code_stud) as count_students
from groups_ g 
join students s on g.code_group = s.code_group
group by g.name_group;

select s.surname, s.name, avg(p.estimate) as avg_estimate
from students s
join progress p on s.code_stud = p.code_stud
where p.date_exam between '2003-01-05' and '2003-01-25'
group by s.surname, s.name;

select name_lector, science, extract(year from age(date_)) as old_years from lectors;

-- Использование функций совместно с подзапросом
select p.*, s.surname, s.name
from progress p
join students s on p.code_stud = s.code_stud
where p.date_exam = (select max(date_exam)
from progress);

select g.name_group from groups_ g
join students s on g.code_group = s.code_group 
group by g.name_group 
having count(s.code_stud) > 25;

-- Использование квантора существования в запросах
select s.Surname, s.Name, s.Lastname from students s
where not exists (select 1 from progress p where p.code_stud = s.code_stud and p.estimate = 2);

select s.Surname, s.Name, s.Lastname from students s
where exists (select 1 from progress p where p.code_stud = s.code_stud and p.estimate = 2);

select s.Surname, s.Name, s.Lastname from students s
where exists (select 1 from progress p where p.code_stud = s.code_stud and p.estimate = 5);

-- Оператор обработки данных Update
update groups_ set num_course = num_course + 1
where current_date = date '2024-09-01';

update students set lastname = 'нет сведений'
where lastname is null or lastname = '';

update subjects set name_subject = 'Математический анализ'
where name_subject = 'Высшая математика';

-- Оператор обработки данных Insert
insert into Progress (Code_progress, Code_stud, Code_subject, Code_lector, Date_exam, Estimate)
values (
    (select max(Code_progress) + 1 from Progress), 
    45, 12, 11, '2003-03-12', null
);

insert into lectors (code_lector, name_lector, science)
values (
    (select coalesce(max(cast(code_lector as integer)), 0) + 1 from lectors),
    'Петров Савелий Яковлевич',
    'к.т.н.'
);

-- Оператор обработки данных Delete
delete from students
where code_group in (35, 15, 19);

delete from subjects
where name_subject is null or name_subject = '';

delete from progress
where date_exam is null;


