"""Synthetic resume generator.

Real labelled resumes are private, so we synthesise realistic ones from role
profiles. Roles deliberately overlap (e.g. Full Stack vs Frontend/Backend, ML vs
Data Science) and 3% of labels are flipped, so the task is not trivially separable.
Swap `build_dataset` for your own CSV loader to train on real data.
"""
import random

from careerlens.skills import ROLE_PHRASES, ROLE_PROFILES, SKILLS

OPENERS = ["Motivated engineering graduate", "Results driven professional", "Final year student",
           "Self taught developer", "Detail oriented problem solver", "Recent graduate"]
EDU = ["B.E. in Computer Science", "B.Tech in Information Technology", "M.Sc. in Computer Applications",
       "B.Sc. in Mathematics"]
GENERIC = ["Strong communication and teamwork skills", "Completed capstone project with a team of four",
           "Participated in hackathons and open source", "Quick learner who enjoys new challenges",
           "Led a college technical club", "Internship experience at a startup"]


def _alias(skill, rng):
    return rng.choice(SKILLS[skill][1] + [skill])


def make_resume(role, rng):
    core = ROLE_PROFILES[role]
    others = [s for r, p in ROLE_PROFILES.items() if r != role for s in p]
    chosen = [s for s in core if rng.random() < 0.6]
    chosen += [s for s in rng.sample(others, k=rng.randint(1, 4))]
    chosen += [s for s in rng.sample(list(SKILLS), k=rng.randint(0, 2))]
    rng.shuffle(chosen)
    chosen = list(dict.fromkeys(chosen)) or [rng.choice(core)]

    parts = [rng.choice(OPENERS) + ".", f"Education: {rng.choice(EDU)}."]
    parts.append("Skills: " + ", ".join(_alias(s, rng) for s in chosen) + ".")
    for phrase in rng.sample(ROLE_PHRASES[role], k=rng.randint(1, 3)):
        sk = rng.sample(chosen, k=min(len(chosen), 2))
        parts.append(f"Experience: {phrase} using " + " and ".join(_alias(s, rng) for s in sk) + ".")
    parts += rng.sample(GENERIC, k=rng.randint(1, 3))
    return " ".join(parts)


def build_dataset(n_per_role=350, seed=42, label_noise=0.03):
    rng = random.Random(seed)
    roles = list(ROLE_PROFILES)
    texts, labels = [], []
    for role in roles:
        for _ in range(n_per_role):
            texts.append(make_resume(role, rng))
            labels.append(rng.choice(roles) if rng.random() < label_noise else role)
    return texts, labels
