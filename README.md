# Multi-Agentic-Mafia-Simulation: Analyzing LLM Biases in Trust-Based Social Games

## Abstract
Large Language Models (LLMs) have rapidly evolved, demonstrating remarkable capabilities across various domains, but concerns about bias in their outputs remain a significant issue. Since these models are trained on extensive datasets sourced from the web, human biases embedded in the data can influence their predictions and decisions. This project aims to detect and analyze the biases exhibited by LLMs towards different demographics, focusing particularly on trust dynamics through a modified Mafia game framework. Our research quantifies and reveals inherent biases in LLM behavior and decisions related to protected demographic groups, examining both biases projected when assuming particular demographics and biases exhibited towards specific demographics and stereotypes.

## Introduction
Large Language Models (LLMs), like GPT and similar architectures, have made significant strides in recent years, demonstrating exceptional capabilities in natural language understanding and generation. However, their reliance on massive datasets raises concerns about the presence of biases in their responses. This project explores how LLMs exhibit bias, particularly in trust-based decisions involving different demographic groups and stereotypes, using a modified version of the social deduction game Mafia as our experimental framework.

Our approach combines traditional trust games like the Prisoner's Dilemma with the complex social dynamics of Mafia, where AI agents represent different roles and demographics. Through this framework, we analyze:
- How LLMs make trust-related decisions based on demographic personas
- The influence of prompts in shaping LLM decisions
- Empirical estimation of probability distributions in decision-making across demographics
- The distinction between prompt-induced and inherent model biases

## Background
Recent research has highlighted several key areas relevant to our study:
- The multifaceted nature of bias and fairness issues in LLMs
- LLM behavior in game-theoretic contexts, particularly in strategic interactions
- Internal decision-making patterns of LLMs under uncertainty
- Methods for detecting and auditing harmful or biased content in LLM outputs

## Project Overview
The Multi-Agentic Mafia Simulation features AI agents representing different roles (Mafia members, civilians, detectives, and doctors) while also incorporating demographic variables. By leveraging LLMs for natural language understanding and generation, each agent engages in strategic dialogue and behaviors that allow us to analyze:
- Trust dynamics between different demographic groups
- Decision-making patterns in high-stakes situations
- The influence of role and demographic information on agent behavior
- Bias manifestation in cooperative versus competitive scenarios

## Methodology
Our research employs a multi-faceted approach:
1. Demographic Persona Assignment: Agents are assigned various demographic characteristics
2. Trust-Based Interactions: Implementation of multiple trust games within the Mafia framework
3. Bias Analysis: Systematic evaluation of decision patterns and trust dynamics
4. Prompt Engineering: Careful design of prompts to isolate model bias from prompt bias

## Technical Implementation
The simulation leverages advanced prompt engineering techniques to:
- Guide agent decision-making processes
- Enable natural language interactions between agents
- Create dynamic and evolving game scenarios
- Collect and analyze bias-related data

## Research Goals
1. Quantify demographic-based trust biases in LLM decision-making
2. Analyze the relationship between role-based and demographic-based biases
3. Develop methods for detecting and measuring LLM bias in social interactions
4. Contribute to the broader understanding of bias in AI systems

## Expected Outcomes
This research aims to:
- Provide empirical data on LLM bias in trust-based decisions
- Develop new methodologies for bias detection in social AI systems
- Contribute to the development of more equitable AI systems
- Advance our understanding of LLM behavior in complex social scenarios
